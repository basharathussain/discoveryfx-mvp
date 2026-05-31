"""Stores router. Phase 1: list/connect placeholder. eBay OAuth wired in Phase 3."""
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_user
from api.db import get_db
from api.models.stores import Store
from api.models.users import User

router = APIRouter()


class StoreOut(BaseModel):
    id: int
    platform: str
    store_name: str
    region: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CreateStubStoreRequest(BaseModel):
    store_name: str = "My eBay UK Store"
    region: str = "GB"


@router.get("", response_model=list[StoreOut])
async def list_stores(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = (await db.execute(select(Store).where(Store.user_id == user.id))).scalars().all()
    return [StoreOut.model_validate(r) for r in rows]


@router.post("/stub", response_model=StoreOut, status_code=201)
async def create_stub_store(
    payload: CreateStubStoreRequest,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Phase-1 helper: create a placeholder store without OAuth so the UI flow works.
    Real OAuth comes in Phase 3 — this endpoint will be removed when /ebay/connect is wired."""
    store = Store(
        user_id=user.id, platform="ebay", store_name=payload.store_name,
        region=payload.region, status="connected_stub",
    )
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return StoreOut.model_validate(store)


# Placeholders for eBay OAuth (Phase 3)
@router.get("/ebay/connect")
async def ebay_connect_start():
    raise HTTPException(status_code=501, detail="eBay OAuth not yet implemented (Phase 3)")


@router.get("/ebay/callback")
async def ebay_callback(code: Optional[str] = None, state: Optional[str] = None):
    raise HTTPException(status_code=501, detail="eBay OAuth not yet implemented (Phase 3)")
