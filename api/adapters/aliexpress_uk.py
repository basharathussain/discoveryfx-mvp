"""AliExpress UK adapter — Phase 2.

In MVP Phase 1 this exists as the contract only; real scraping is wired in Phase 2.
Uses curl_cffi (cheap tier) with GB region cookie, falling back to Playwright when the
SSR page lacks markers (the well-known AliExpress soft-block / hydration pattern).
"""
from decimal import Decimal

from api.adapters.base import SupplierAdapter, SupplierProductRaw, SupplierProductDetailRaw


class AliExpressUKAdapter(SupplierAdapter):
    source = "aliexpress_uk"
    currency = "GBP"

    GB_COOKIE = "aep_usuc_f=site=glo&province=&city=&c_tp=GBP&region=GB&b_locale=en_GB&ae_u_p_s=2"

    def search(self, query: str, page: int = 1) -> list[SupplierProductRaw]:
        raise NotImplementedError("Phase 2: AliExpress UK search not yet implemented")

    def fetch_detail(self, product_url: str) -> SupplierProductDetailRaw:
        raise NotImplementedError("Phase 2: AliExpress UK detail not yet implemented")

    def estimate_shipping_uk(self, product_url: str) -> Decimal:
        raise NotImplementedError("Phase 2: AliExpress UK shipping estimate not yet implemented")
