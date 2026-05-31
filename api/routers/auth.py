from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.deps import current_user
from api.auth.jwt import make_access_token, make_refresh_token
from api.auth.password import hash_password, verify_password
from api.db import get_db
from api.models.users import User
from api.models.markup_rules import MarkupRule
from api.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserOut

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    existing = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.flush()

    # Sensible default markup rule
    db.add(MarkupRule(user_id=user.id))
    await db.commit()

    return TokenResponse(
        access_token=make_access_token(user.id),
        refresh_token=make_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    user = (await db.execute(select(User).where(User.email == payload.email))).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(
        access_token=make_access_token(user.id),
        refresh_token=make_refresh_token(user.id),
    )


@router.get("/me", response_model=UserOut)
async def me(user: Annotated[User, Depends(current_user)]):
    return user
