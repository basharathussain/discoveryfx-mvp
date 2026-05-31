"""Supplier adapter contract.

Every supplier source implements this. Adapters return raw DTOs only —
mapping to the SQLAlchemy SupplierProduct model is done in normalizer.py
so per-source quirks never leak into the rest of the codebase.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, Protocol


@dataclass
class SupplierProductRaw:
    source: str
    supplier_name: str
    product_url: str
    title: str
    cost_price: Decimal
    currency: str = "GBP"
    shipping_cost: Decimal = Decimal(0)
    external_id: Optional[str] = None
    image: Optional[str] = None
    category: Optional[str] = None
    orders_count: int = 0
    reviews_count: int = 0
    supplier_rating: Optional[float] = None
    extra: dict = field(default_factory=dict)


@dataclass
class SupplierProductDetailRaw(SupplierProductRaw):
    description: str = ""
    images: list[str] = field(default_factory=list)
    variants: list[dict] = field(default_factory=list)


class SupplierAdapter(Protocol):
    source: str
    currency: str

    async def search(self, query: str, page: int = 1) -> list[SupplierProductRaw]: ...

    async def fetch_detail(self, product_url: str) -> SupplierProductDetailRaw: ...

    def estimate_shipping_uk(self, product_url: str) -> Decimal: ...
