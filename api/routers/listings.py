from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_user
from api.db import get_db
from api.models.listings import Listing
from api.models.markup_rules import MarkupRule
from api.models.supplier_products import SupplierProduct
from api.models.users import User
from api.schemas.listings import CreateListingRequest, ListingOut, UpdateListingRequest

router = APIRouter()


def _suggest_price(cost: Decimal, shipping: Decimal, markup_pct: Decimal) -> Decimal:
    landed = (cost or Decimal(0)) + (shipping or Decimal(0))
    return (landed * (Decimal(1) + markup_pct / Decimal(100))).quantize(Decimal("0.01"))


@router.get("", response_model=list[ListingOut])
async def list_user_listings(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = None,
):
    stmt = select(Listing).where(Listing.user_id == user.id).order_by(Listing.created_at.desc())
    if status:
        stmt = stmt.where(Listing.status == status)
    rows = (await db.execute(stmt)).scalars().all()
    return [ListingOut.model_validate(r) for r in rows]


@router.post("", response_model=ListingOut, status_code=201)
async def create_listing(
    payload: CreateListingRequest,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    sp = (await db.execute(
        select(SupplierProduct).where(SupplierProduct.id == payload.supplier_product_id)
    )).scalar_one_or_none()
    if not sp:
        raise HTTPException(status_code=404, detail="Supplier product not found")

    rule = (await db.execute(
        select(MarkupRule).where(MarkupRule.user_id == user.id)
    )).scalar_one_or_none()
    markup_pct = rule.default_markup_pct if rule else Decimal("35.00")

    selling_price = payload.selling_price or _suggest_price(sp.cost_price, sp.shipping_cost, markup_pct)
    landed = (sp.cost_price or Decimal(0)) + (sp.shipping_cost or Decimal(0))
    profit_margin = (selling_price - landed).quantize(Decimal("0.01"))

    listing = Listing(
        user_id=user.id,
        supplier_product_id=sp.id,
        title=payload.title or sp.title[:80],
        description=payload.description or "",
        currency=sp.currency,
        selling_price=selling_price,
        profit_margin=profit_margin,
        status="draft",
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return ListingOut.model_validate(listing)


@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(
    listing_id: int,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = (await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.user_id == user.id)
    )).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingOut.model_validate(row)


@router.post("/{listing_id}/publish", response_model=ListingOut)
async def publish_listing(
    listing_id: int,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Publish a draft to eBay UK (sandbox).

    Phase-1 stub: returns 501 unless EBAY_CLIENT_ID is configured.
    Phase-3 will wire the real Inventory → Offer → Publish flow.
    """
    from api.config import settings as cfg
    row = (await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.user_id == user.id)
    )).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")
    if not cfg.ebay_client_id:
        raise HTTPException(
            status_code=501,
            detail="eBay credentials not configured. Set EBAY_CLIENT_ID / EBAY_CLIENT_SECRET in .env and connect a store first.",
        )
    raise HTTPException(status_code=501, detail="Publish flow lands in Phase 3.")


@router.patch("/{listing_id}", response_model=ListingOut)
async def update_listing(
    listing_id: int,
    payload: UpdateListingRequest,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = (await db.execute(
        select(Listing).where(Listing.id == listing_id, Listing.user_id == user.id)
    )).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")

    if payload.title is not None:        row.title = payload.title
    if payload.description is not None:  row.description = payload.description
    if payload.store_id is not None:     row.store_id = payload.store_id
    if payload.selling_price is not None:
        sp = (await db.execute(
            select(SupplierProduct).where(SupplierProduct.id == row.supplier_product_id)
        )).scalar_one()
        landed = (sp.cost_price or Decimal(0)) + (sp.shipping_cost or Decimal(0))
        row.selling_price = payload.selling_price
        row.profit_margin = (payload.selling_price - landed).quantize(Decimal("0.01"))

    await db.commit()
    await db.refresh(row)
    return ListingOut.model_validate(row)
