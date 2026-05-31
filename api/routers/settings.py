from decimal import Decimal
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_user
from api.db import get_db
from api.models.markup_rules import MarkupRule
from api.models.users import User

router = APIRouter()


class MarkupRuleOut(BaseModel):
    id: int
    default_markup_pct: Decimal
    currency: str
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateMarkupRequest(BaseModel):
    default_markup_pct: Decimal = Field(ge=0, le=500)


@router.get("/markup", response_model=MarkupRuleOut)
async def get_markup(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rule = (await db.execute(
        select(MarkupRule).where(MarkupRule.user_id == user.id)
    )).scalar_one_or_none()
    if not rule:
        rule = MarkupRule(user_id=user.id)
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
    return MarkupRuleOut.model_validate(rule)


@router.put("/markup", response_model=MarkupRuleOut)
async def update_markup(
    payload: UpdateMarkupRequest,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rule = (await db.execute(
        select(MarkupRule).where(MarkupRule.user_id == user.id)
    )).scalar_one_or_none()
    if not rule:
        rule = MarkupRule(user_id=user.id)
        db.add(rule)
    rule.default_markup_pct = payload.default_markup_pct
    await db.commit()
    await db.refresh(rule)
    return MarkupRuleOut.model_validate(rule)
