from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CreateListingRequest(BaseModel):
    supplier_product_id: int
    title: Optional[str] = None        # if absent, defaults from supplier title
    description: Optional[str] = None
    selling_price: Optional[Decimal] = None  # if absent, derived from markup rule


class UpdateListingRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    selling_price: Optional[Decimal] = None
    store_id: Optional[int] = None


class ListingOut(BaseModel):
    id: int
    user_id: int
    supplier_product_id: int
    store_id: Optional[int]
    title: str
    description: str
    currency: str
    selling_price: Decimal
    profit_margin: Decimal
    status: str
    ebay_item_id: Optional[str]
    ebay_offer_id: Optional[str]
    ebay_sku: Optional[str]
    publish_error: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
