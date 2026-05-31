from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt as pyjwt

from api.config import settings


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": _now(),
        "exp": _now() + timedelta(minutes=settings.access_token_minutes),
    }
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def make_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": _now(),
        "exp": _now() + timedelta(days=settings.refresh_token_days),
    }
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return pyjwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except pyjwt.PyJWTError:
        return None
