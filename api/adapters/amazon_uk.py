"""Amazon UK adapter — Phase 2.

Public product-page scraping on amazon.co.uk. ASIN is the external_id.
Phase 2 will wire curl_cffi against amazon.co.uk with a UK-locale cookie.
"""
from decimal import Decimal

from api.adapters.base import SupplierAdapter, SupplierProductRaw, SupplierProductDetailRaw


class AmazonUKAdapter(SupplierAdapter):
    source = "amazon_uk"
    currency = "GBP"

    BASE_URL = "https://www.amazon.co.uk"

    def search(self, query: str, page: int = 1) -> list[SupplierProductRaw]:
        raise NotImplementedError("Phase 2: Amazon UK search not yet implemented")

    def fetch_detail(self, product_url: str) -> SupplierProductDetailRaw:
        raise NotImplementedError("Phase 2: Amazon UK detail not yet implemented")

    def estimate_shipping_uk(self, product_url: str) -> Decimal:
        raise NotImplementedError("Phase 2: Amazon UK shipping estimate not yet implemented")
