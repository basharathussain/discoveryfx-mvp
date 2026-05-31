from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_user
from api.db import get_db
from api.models.orders import Order
from api.models.stores import Store
from api.models.users import User

router = APIRouter()


class OrderOut(BaseModel):
    id: int
    store_id: int
    listing_id: Optional[int]
    ebay_order_id: str
    buyer_name: Optional[str]
    currency: str
    total: Decimal
    order_status: str
    supplier_product_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[OrderOut])
async def list_orders(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Pull orders that belong to stores owned by this user
    store_ids = (await db.execute(
        select(Store.id).where(Store.user_id == user.id)
    )).scalars().all()
    if not store_ids:
        return []
    rows = (await db.execute(
        select(Order).where(Order.store_id.in_(store_ids)).order_by(Order.created_at.desc())
    )).scalars().all()
    return [OrderOut.model_validate(r) for r in rows]
