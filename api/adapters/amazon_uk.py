"""Amazon UK adapter.

Source-specific parsing for amazon.co.uk SSR pages. All Amazon-only logic stays
inside this module — selector patterns, captcha markers, GBP price parsing.

Endpoints used:
- Search: https://www.amazon.co.uk/s?k={query}
- Detail: https://www.amazon.co.uk/dp/{ASIN}

Amazon's HTML is structured but volatile — selectors drift. We use multiple
fallbacks per field and silently skip cards we can't parse, never raise.
"""
import re
import urllib.parse
from decimal import Decimal, InvalidOperation
from typing import Optional

from bs4 import BeautifulSoup

from api.adapters._http import FetchResult, fetch_html
from api.adapters.base import SupplierAdapter, SupplierProductDetailRaw, SupplierProductRaw


# ── Amazon-only bot-wall markers ──────────────────────────────────────────────

_BOT_MARKERS = (
    "/errors/validateCaptcha",
    "Enter the characters you see below",
    'name="amzn"',                          # captcha form field
    "To discuss automated access to Amazon",
    "Robot Check",
    "awswaf.com",                           # AWS WAF JS challenge (most common today)
    "AwsWafIntegration",                    # AWS WAF inline script
    "window.gokuProps",                     # AWS WAF token payload
    "challenge-container",                  # AWS WAF mount point
)


def _is_bot_walled(html: str, final_url: str) -> Optional[str]:
    if "/errors/validateCaptcha" in final_url:
        return "Amazon CAPTCHA redirect"
    sample = html[:8000]
    for m in _BOT_MARKERS:
        if m in sample:
            if "awswaf" in m.lower() or "AwsWaf" in m or "gokuProps" in m or "challenge-container" in m:
                return "Amazon AWS WAF challenge (requires Playwright — JS proof-of-work)"
            return f"Amazon bot-wall: {m}"
    # Very small responses with no real content are almost always interstitials.
    if len(html) < 4000 and "amazon" in (final_url or "").lower() and "search" in (final_url or ""):
        return "Amazon returned a stub page (likely soft block)"
    return None


# ── Helpers --------------------------------------------------------------------

def _to_decimal(s: str) -> Optional[Decimal]:
    s = (s or "").replace(",", "").replace("£", "").strip()
    if not s:
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _extract_price(card) -> Optional[Decimal]:
    """Try several Amazon price patterns in priority order."""
    # 1. The newer offscreen full-price node
    el = card.select_one("span.a-price > span.a-offscreen")
    if el and el.text:
        d = _to_decimal(el.text)
        if d:
            return d
    # 2. The whole/fraction split
    whole = card.select_one("span.a-price-whole")
    frac = card.select_one("span.a-price-fraction")
    if whole:
        w = whole.get_text(strip=True).rstrip(".")
        f = frac.get_text(strip=True) if frac else "00"
        d = _to_decimal(f"{w}.{f}")
        if d:
            return d
    # 3. Plain regex against the card HTML — last resort
    m = re.search(r"£\s*([\d,]+\.\d{1,2})", str(card))
    return _to_decimal(m.group(1)) if m else None


def _extract_title(card) -> str:
    for sel in ("h2 a span", "h2 span", "h2 a", "h2"):
        el = card.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return ""


def _extract_image(card) -> Optional[str]:
    el = card.select_one("img.s-image, img[data-image-latency]")
    if el and el.get("src"):
        return el["src"]
    return None


def _extract_asin(card) -> Optional[str]:
    asin = card.get("data-asin")
    if asin and re.fullmatch(r"[A-Z0-9]{10}", asin):
        return asin
    return None


def _extract_rating(card) -> Optional[float]:
    el = card.select_one("span.a-icon-alt")
    if el:
        m = re.search(r"([\d.]+)\s+out of\s+5", el.get_text())
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    return None


def _extract_review_count(card) -> int:
    # Looks like "1,234" inside the reviews span next to the rating
    el = card.select_one("span.a-size-base.s-underline-text") or card.select_one("a span.a-size-base")
    if el:
        m = re.search(r"([\d,]+)", el.get_text())
        if m:
            try:
                return int(m.group(1).replace(",", ""))
            except ValueError:
                pass
    return 0


# ── Adapter --------------------------------------------------------------------

class AmazonUKAdapter(SupplierAdapter):
    source = "amazon_uk"
    currency = "GBP"

    BASE = "https://www.amazon.co.uk"
    SEARCH_URL = BASE + "/s?k={q}"
    ITEM_URL = BASE + "/dp/{asin}"

    # Amazon prefers a "real" cookie hint that the visitor accepted UK locale.
    UK_COOKIE = "i18n-prefs=GBP; lc-acbuk=en_GB"

    async def search(self, query: str, page: int = 1) -> list[SupplierProductRaw]:
        q = urllib.parse.quote_plus(query.strip())
        url = self.SEARCH_URL.format(q=q)
        if page > 1:
            url += f"&page={page}"

        result: FetchResult = await fetch_html(
            url, accept_lang="en-GB,en;q=0.9", cookie=self.UK_COOKIE,
            referer=self.BASE + "/",
        )
        if not result.ok:
            raise RuntimeError(f"Amazon UK search failed: {result.error or result.status_code}")
        walled = _is_bot_walled(result.html, result.final_url)
        if walled:
            raise RuntimeError(walled)

        soup = BeautifulSoup(result.html, "html.parser")
        cards = soup.select('div[data-component-type="s-search-result"][data-asin]')

        out: list[SupplierProductRaw] = []
        for card in cards:
            asin = _extract_asin(card)
            title = _extract_title(card)
            price = _extract_price(card)
            if not (asin and title and price):
                continue  # incomplete — skip
            out.append(SupplierProductRaw(
                source=self.source,
                supplier_name="Amazon UK",
                product_url=self.ITEM_URL.format(asin=asin),
                title=title,
                cost_price=price,
                currency=self.currency,
                shipping_cost=Decimal(0),  # Amazon UK is usually Prime-free for sellers
                external_id=asin,
                image=_extract_image(card),
                category=None,
                orders_count=0,
                reviews_count=_extract_review_count(card),
                supplier_rating=_extract_rating(card),
            ))
            if len(out) >= 60:
                break
        return out

    async def fetch_detail(self, product_url: str) -> SupplierProductDetailRaw:
        result = await fetch_html(
            product_url, accept_lang="en-GB,en;q=0.9", cookie=self.UK_COOKIE,
            referer=self.BASE + "/",
        )
        if not result.ok:
            raise RuntimeError(f"Amazon UK detail failed: {result.error or result.status_code}")
        walled = _is_bot_walled(result.html, result.final_url)
        if walled:
            raise RuntimeError(walled)

        soup = BeautifulSoup(result.html, "html.parser")
        title_el = soup.select_one("#productTitle") or soup.select_one("span#productTitle")
        title = title_el.get_text(strip=True) if title_el else ""

        # Price — try multiple Amazon layouts
        price = None
        for sel in ("span.a-price.a-text-price.a-size-medium.apexPriceToPay span.a-offscreen",
                    "span.a-price > span.a-offscreen",
                    "#priceblock_ourprice",
                    "#priceblock_dealprice"):
            el = soup.select_one(sel)
            if el:
                price = _to_decimal(el.get_text(strip=True))
                if price:
                    break

        if not price:
            m = re.search(r"£\s*([\d,]+\.\d{1,2})", result.html)
            price = _to_decimal(m.group(1)) if m else None

        if not price:
            raise RuntimeError("Amazon UK detail: no GBP price found")

        # Image
        img_el = soup.select_one("img#landingImage, img#imgBlkFront")
        image = img_el.get("src") if img_el else None

        asin_m = re.search(r"/dp/([A-Z0-9]{10})", product_url)
        asin = asin_m.group(1) if asin_m else None

        return SupplierProductDetailRaw(
            source=self.source,
            supplier_name="Amazon UK",
            product_url=product_url,
            title=title or "(untitled)",
            cost_price=price,
            currency=self.currency,
            shipping_cost=Decimal(0),
            external_id=asin,
            image=image,
            category=None,
            orders_count=0,
            reviews_count=0,
            supplier_rating=None,
        )

    def estimate_shipping_uk(self, product_url: str) -> Decimal:
        """Amazon UK domestic shipping is usually £0 for Prime-eligible items,
        otherwise £2–5. Full estimate requires the offer/listing API. Return 0."""
        return Decimal(0)
