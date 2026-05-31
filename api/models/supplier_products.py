from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey, Float, func, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from api.db import Base


class SupplierProduct(Base):
    """A single supplier listing — the unit of opportunity (no dedup across sources)."""
    __tablename__ = "supplier_products"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Identity / source
    source: Mapped[str] = mapped_column(String(32), index=True, nullable=False)        # aliexpress_uk | amazon_uk
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    supplier_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    product_url: Mapped[str] = mapped_column(Text, nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)  # ASIN, AE id, etc.

    # Content
    title: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    shipping_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    # Market signal
    orders_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reviews_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Scores (0–100) + explainable inputs
    trend_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    trend_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    supplier_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    supplier_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    margin_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    margin_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    competition_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    competition_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    overall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0, index=True)
    overall_inputs: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    discovered_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
