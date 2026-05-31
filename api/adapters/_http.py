"""Shared HTTP plumbing for supplier adapters.

Source-agnostic — only knows about Chrome impersonation, region cookies, and
generic bot-wall markers. Source-specific parsing lives in each adapter module.
"""
import logging
import random
from dataclasses import dataclass
from typing import Optional

from curl_cffi import requests as cffi_requests  # type: ignore

log = logging.getLogger(__name__)


# Chrome impersonation profiles supported by curl_cffi 0.7.x.
# We randomise per request so JA3/H2 fingerprints rotate. Profiles beyond
# chrome124 require a newer curl_cffi build (0.8+); keep this list in sync
# with `from curl_cffi.requests.session import BrowserType`.
CHROME_PROFILES = ["chrome119", "chrome120", "chrome123", "chrome124"]

# Region presets used by both adapters. AliExpress reads the `aep_usuc_f` cookie
# to set currency + locale; Amazon uses host-level locale (amazon.co.uk).
GB_ALIEXPRESS_COOKIE = (
    "aep_usuc_f=site=glo&province=&city=&c_tp=GBP&region=GB&b_locale=en_GB&ae_u_p_s=2"
)


@dataclass
class FetchResult:
    """What an HTTP fetch returned. `ok=False` means bot wall, captcha, or error."""
    ok: bool
    status_code: Optional[int] = None
    html: str = ""
    final_url: str = ""
    error: Optional[str] = None


def _headers(accept_lang: str, cookie: str, referer: Optional[str] = None) -> dict:
    h = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": accept_lang,
        "Cookie": cookie,
        "Sec-Fetch-Site": "same-origin" if referer else "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        h["Referer"] = referer
    return h


async def fetch_html(
    url: str,
    *,
    accept_lang: str = "en-GB,en;q=0.9",
    cookie: str = "",
    referer: Optional[str] = None,
    timeout: float = 20.0,
) -> FetchResult:
    """One HTTP GET with random Chrome impersonation. Returns FetchResult.

    Caller is responsible for source-specific bot-wall detection on the
    returned `html` — generic shortcuts (HTTP 403/429/503) are flagged here.
    """
    profile = random.choice(CHROME_PROFILES)
    headers = _headers(accept_lang, cookie, referer)

    try:
        async with cffi_requests.AsyncSession(impersonate=profile, timeout=timeout) as sess:
            resp = await sess.get(url, headers=headers, allow_redirects=True)
    except Exception as e:
        return FetchResult(ok=False, error=f"{type(e).__name__}: {e}")

    html = resp.text or ""
    final_url = str(resp.url)
    status = resp.status_code

    if status in (403, 429, 503):
        return FetchResult(
            ok=False, status_code=status, html=html, final_url=final_url,
            error=f"HTTP {status}",
        )
    if status >= 400:
        return FetchResult(
            ok=False, status_code=status, html=html, final_url=final_url,
            error=f"HTTP {status}",
        )
    return FetchResult(ok=True, status_code=status, html=html, final_url=final_url)
