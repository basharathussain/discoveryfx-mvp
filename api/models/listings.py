from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from api.db import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    supplier_product_id: Mapped[int] = mapped_column(ForeignKey("supplier_products.id"), index=True, nullable=False)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)

    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    selling_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    profit_margin: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)  # absolute GBP

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")   # draft | active | paused | ended | failed
    ebay_item_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ebay_offer_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ebay_sku: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    publish_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
