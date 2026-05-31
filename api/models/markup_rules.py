from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from api.db import Base


class MarkupRule(Base):
    __tablename__ = "markup_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False, unique=True)
    default_markup_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=Decimal("35.00"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
