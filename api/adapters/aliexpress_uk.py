"""AliExpress UK adapter.

Source-specific parsing for aliexpress.com SSR pages with the GB region cookie
(currency = GBP, locale = en_GB). All AliExpress-only logic stays inside this
module — bot-wall markers, price parsing, JSON-in-HTML extraction.

Endpoints used:
- Search:  https://www.aliexpress.com/w/wholesale-{query}.html
- Detail:  https://www.aliexpress.com/item/{external_id}.html
"""
import json
import re
import urllib.parse
from decimal import Decimal, InvalidOperation
from typing import Optional

from api.adapters._http import GB_ALIEXPRESS_COOKIE, FetchResult, fetch_html
from api.adapters.base import SupplierAdapter, SupplierProductDetailRaw, SupplierProductRaw


# ── AliExpress-only bot-wall / soft-block markers ─────────────────────────────

_BOT_MARKERS = (
    "<title>Captcha Interception</title>",
    "_PUNISH_PAGE",
    "punish.aliexpress.com",
    "nocaptcha.aliyun.com",
    "captcha.aliexpress.com",
    "_____tmd_____",          # TMD soft-block path
    'rgv587_flag',            # Alibaba bot-wall comment
    '"action":"captcha"',     # newer punish JSON
)
_BUNDLE_REDIRECT = "ssr/30000"


def _is_bot_walled(html: str, final_url: str) -> Optional[str]:
    sample = html[:6000]
    for m in _BOT_MARKERS:
        if m in sample:
            return f"AliExpress bot-wall: {m}"
    if _BUNDLE_REDIRECT in final_url:
        return "AliExpress bundle redirect"
    return None


# ── Helpers --------------------------------------------------------------------

_GBP_PRICE_RX = re.compile(
    r'"formattedPrice"\s*:\s*"(?:£|GBP\s*|&pound;)\s*([\d,]+(?:\.\d{1,2})?)"'
)
_PRODUCT_BLOCK_RX = re.compile(r'"productId"\s*:\s*"(\d{10,})"')
_RUN_PARAMS_RX = re.compile(r'window\.runParams\s*=\s*({)', re.IGNORECASE)


def _to_decimal(s: str) -> Optional[Decimal]:
    try:
        return Decimal(s.replace(",", "").strip())
    except (InvalidOperation, AttributeError):
        return None


def _normalise_image(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    if url.startswith("//"):
        return "https:" + url
    return url


def _balanced_braces(s: str) -> str:
    """Extract content of a {...} block starting at s[0]=='{', preserving nesting."""
    depth = 0
    for i, ch in enumerate(s):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return s[:i + 1]
    return ""


def _parse_search_modern(html: str) -> list[dict]:
    """Modern SSR: hunt for productId blocks and gather title/image/price nearby."""
    out: list[dict] = []
    seen: set[str] = set()
    for m in _PRODUCT_BLOCK_RX.finditer(html):
        pid = m.group(1)
        if pid in seen:
            continue
        chunk = html[max(0, m.start() - 600):min(len(html), m.end() + 600)]

        title_m = (re.search(r'"displayTitle"\s*:\s*"([^"]+)"', chunk)
                   or re.search(r'"title"\s*:\s*"([^"]+)"', chunk))
        if not title_m:
            continue
        title = title_m.group(1).strip()

        img_m = re.search(r'"imgUrl"\s*:\s*"([^"]+)"', chunk)
        image = _normalise_image(img_m.group(1) if img_m else None)

        price_m = _GBP_PRICE_RX.search(chunk)
        price = _to_decimal(price_m.group(1)) if price_m else None

        orders_m = re.search(r'"tradeDesc"\s*:\s*"(\d[\d,]*)\+? sold"', chunk)
        orders = int(orders_m.group(1).replace(",", "")) if orders_m else 0

        rating_m = re.search(r'"starRating"\s*:\s*"?([\d.]+)"?', chunk)
        try:
            rating = float(rating_m.group(1)) if rating_m else None
        except ValueError:
            rating = None

        seen.add(pid)
        out.append({
            "external_id": pid,
            "title": title,
            "image": image,
            "cost_price": price,
            "orders_count": orders,
            "supplier_rating": rating,
        })
        if len(out) >= 60:
            break
    return out


def _parse_search_legacy(html: str) -> list[dict]:
    """Legacy `window.runParams = { ... }` path — older AliExpress pages."""
    m = _RUN_PARAMS_RX.search(html)
    if not m:
        return []
    block = _balanced_braces(html[m.start(1):])
    if not block:
        return []
    try:
        rp = json.loads(block)
    except Exception:
        return []

    content = (rp.get("data", {}).get("mods", {}).get("itemList", {}).get("content")
               or rp.get("data", {}).get("itemList", {}).get("content")
               or [])
    out: list[dict] = []
    for item in content if isinstance(content, list) else []:
        if not isinstance(item, dict):
            continue
        pid = str(item.get("productId") or item.get("redirectedId") or "")
        if not pid:
            continue
        title_obj = item.get("title", {})
        title = title_obj.get("displayTitle", "") if isinstance(title_obj, dict) else str(title_obj or "")
        if not title:
            continue
        img_obj = item.get("image", {})
        image = _normalise_image(img_obj.get("imgUrl", "") if isinstance(img_obj, dict) else "")

        # Price — handle GBP formatted variants.
        price = None
        prices = item.get("prices", {})
        if isinstance(prices, dict):
            sale = prices.get("salePrice", {})
            if isinstance(sale, dict):
                fp = sale.get("formattedPrice", "")
                pm = re.search(r"([\d,]+\.\d{1,2}|[\d,]+)", fp or "")
                if pm:
                    price = _to_decimal(pm.group(1))

        orders = 0
        trade_obj = item.get("trade", {})
        if isinstance(trade_obj, dict):
            td = trade_obj.get("tradeDesc", "") or ""
            tm = re.search(r"(\d[\d,]*)", td)
            if tm:
                try:
                    orders = int(tm.group(1).replace(",", ""))
                except ValueError:
                    orders = 0

        out.append({
            "external_id": pid,
            "title": title.strip(),
            "image": image,
            "cost_price": price,
            "orders_count": orders,
            "supplier_rating": None,
        })
    return out


def _parse_detail(html: str) -> dict:
    """OG-meta + JSON-in-HTML — best-effort detail extraction."""
    out: dict = {}
    og_title = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', html)
    og_image = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
    out["title"] = og_title.group(1).strip() if og_title else ""
    out["image"] = _normalise_image(og_image.group(1) if og_image else None)

    price_m = _GBP_PRICE_RX.search(html)
    if price_m:
        out["cost_price"] = _to_decimal(price_m.group(1))
    return out


# ── Adapter --------------------------------------------------------------------

class AliExpressUKAdapter(SupplierAdapter):
    source = "aliexpress_uk"
    currency = "GBP"

    BASE = "https://www.aliexpress.com"
    SEARCH_URL = BASE + "/w/wholesale-{q}.html"
    ITEM_URL = BASE + "/item/{external_id}.html"

    async def search(self, query: str, page: int = 1) -> list[SupplierProductRaw]:
        q = urllib.parse.quote_plus(query.strip())
        url = self.SEARCH_URL.format(q=q)
        if page > 1:
            url += f"?page={page}"

        result: FetchResult = await fetch_html(
            url, accept_lang="en-GB,en;q=0.9", cookie=GB_ALIEXPRESS_COOKIE,
        )
        if not result.ok:
            raise RuntimeError(f"AliExpress UK search failed: {result.error or result.status_code}")
        walled = _is_bot_walled(result.html, result.final_url)
        if walled:
            raise RuntimeError(walled)

        # Try legacy first (richer data when present), then modern.
        items = _parse_search_legacy(result.html) or _parse_search_modern(result.html)

        out: list[SupplierProductRaw] = []
        for it in items:
            if it["cost_price"] is None:
                continue  # skip rows without GBP price — they'll be useless for margin scoring
            out.append(SupplierProductRaw(
                source=self.source,
                supplier_name="AliExpress UK",
                product_url=self.ITEM_URL.format(external_id=it["external_id"]),
                title=it["title"],
                cost_price=it["cost_price"],
                currency=self.currency,
                shipping_cost=Decimal(0),
                external_id=it["external_id"],
                image=it.get("image"),
                category=None,
                orders_count=it.get("orders_count", 0) or 0,
                reviews_count=0,
                supplier_rating=it.get("supplier_rating"),
            ))
        return out

    async def fetch_detail(self, product_url: str) -> SupplierProductDetailRaw:
        result = await fetch_html(
            product_url, accept_lang="en-GB,en;q=0.9", cookie=GB_ALIEXPRESS_COOKIE,
            referer=self.BASE + "/",
        )
        if not result.ok:
            raise RuntimeError(f"AliExpress UK detail failed: {result.error or result.status_code}")
        walled = _is_bot_walled(result.html, result.final_url)
        if walled:
            raise RuntimeError(walled)

        parsed = _parse_detail(result.html)
        ext_id_m = re.search(r"/item/(\d{10,})\.html", product_url)
        ext_id = ext_id_m.group(1) if ext_id_m else None

        if parsed.get("cost_price") is None:
            raise RuntimeError("AliExpress UK detail: no GBP price found in SSR — needs Playwright path")

        return SupplierProductDetailRaw(
            source=self.source,
            supplier_name="AliExpress UK",
            product_url=product_url,
            title=parsed.get("title", "(untitled)"),
            cost_price=parsed["cost_price"],
            currency=self.currency,
            shipping_cost=Decimal(0),
            external_id=ext_id,
            image=parsed.get("image"),
            category=None,
            orders_count=0,
            reviews_count=0,
            supplier_rating=None,
        )

    def estimate_shipping_uk(self, product_url: str) -> Decimal:
        """Quick heuristic — AliExpress to UK is typically free for cheap items,
        £1–3 for heavier. Full shipping calc requires the signed mtop API which
        needs Playwright. For MVP scoring purposes, return 0."""
        return Decimal(0)
