from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from api.db import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True, nullable=False)
    listing_id: Mapped[Optional[int]] = mapped_column(ForeignKey("listings.id"), index=True, nullable=True)

    ebay_order_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    buyer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    buyer_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    supplier_product_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
