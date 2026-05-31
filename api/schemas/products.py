from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class SupplierProductOut(BaseModel):
    id: int
    source: str
    supplier_name: str
    supplier_rating: Optional[float] = None
    product_url: str
    external_id: Optional[str] = None
    title: str
    image: Optional[str] = None
    category: Optional[str] = None
    currency: str
    cost_price: Decimal
    shipping_cost: Decimal
    orders_count: int
    reviews_count: int
    trend_score: float
    supplier_score: float
    margin_score: float
    competition_score: float
    overall_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierProductDetailOut(SupplierProductOut):
    trend_inputs: dict
    supplier_inputs: dict
    margin_inputs: dict
    competition_inputs: dict
    overall_inputs: dict


class ProductListOut(BaseModel):
    items: list[SupplierProductOut]
    total: int
    page: int
    page_size: int
