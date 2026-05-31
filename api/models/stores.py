from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from api.db import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(32), nullable=False, default="ebay")   # ebay only in MVP
    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(8), nullable=False, default="GB")        # eBay UK = EBAY_GB

    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="connected")  # connected | expired | revoked
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
