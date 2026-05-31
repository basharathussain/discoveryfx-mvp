from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_user
from api.db import get_db
from api.models.supplier_products import SupplierProduct
from api.models.users import User
from api.schemas.products import ProductListOut, SupplierProductDetailOut, SupplierProductOut

router = APIRouter()


@router.get("", response_model=ProductListOut)
async def list_products(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    q: Optional[str] = Query(None, description="Full-text query on title"),
    source: Optional[str] = Query(None, description="aliexpress_uk | amazon_uk"),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_orders: Optional[int] = None,
    min_rating: Optional[float] = None,
    min_trend: Optional[float] = None,
    min_margin: Optional[float] = None,
    min_overall: Optional[float] = None,
    sort: str = Query("overall_score", description="overall_score | margin_score | trend_score | created_at"),
    order: str = Query("desc", description="asc | desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    conditions = []
    if q:
        conditions.append(SupplierProduct.title.ilike(f"%{q}%"))
    if source:
        conditions.append(SupplierProduct.source == source)
    if category:
        conditions.append(SupplierProduct.category == category)
    if min_price is not None:
        conditions.append(SupplierProduct.cost_price >= min_price)
    if max_price is not None:
        conditions.append(SupplierProduct.cost_price <= max_price)
    if min_orders is not None:
        conditions.append(SupplierProduct.orders_count >= min_orders)
    if min_rating is not None:
        conditions.append(SupplierProduct.supplier_rating >= min_rating)
    if min_trend is not None:
        conditions.append(SupplierProduct.trend_score >= min_trend)
    if min_margin is not None:
        conditions.append(SupplierProduct.margin_score >= min_margin)
    if min_overall is not None:
        conditions.append(SupplierProduct.overall_score >= min_overall)

    where_clause = and_(*conditions) if conditions else None

    # Sort column
    sort_col = {
        "overall_score": SupplierProduct.overall_score,
        "margin_score":  SupplierProduct.margin_score,
        "trend_score":   SupplierProduct.trend_score,
        "created_at":    SupplierProduct.created_at,
        "orders_count":  SupplierProduct.orders_count,
        "cost_price":    SupplierProduct.cost_price,
    }.get(sort, SupplierProduct.overall_score)
    sort_col = sort_col.desc() if order == "desc" else sort_col.asc()

    # Count
    count_stmt = select(func.count(SupplierProduct.id))
    if where_clause is not None:
        count_stmt = count_stmt.where(where_clause)
    total = (await db.execute(count_stmt)).scalar_one()

    # Page
    stmt = select(SupplierProduct).order_by(sort_col).offset((page - 1) * page_size).limit(page_size)
    if where_clause is not None:
        stmt = stmt.where(where_clause)
    rows = (await db.execute(stmt)).scalars().all()

    return ProductListOut(
        items=[SupplierProductOut.model_validate(r) for r in rows],
        total=total, page=page, page_size=page_size,
    )


@router.get("/categories", response_model=list[str])
async def list_categories(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(SupplierProduct.category).where(SupplierProduct.category.is_not(None)).distinct().order_by(SupplierProduct.category)
    rows = (await db.execute(stmt)).scalars().all()
    return [r for r in rows if r]


@router.get("/{product_id}", response_model=SupplierProductDetailOut)
async def get_product(
    product_id: int,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    row = (await db.execute(select(SupplierProduct).where(SupplierProduct.id == product_id))).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return SupplierProductDetailOut.model_validate(row)
