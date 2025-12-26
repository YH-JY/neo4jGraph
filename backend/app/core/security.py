from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .settings import get_settings


auth_scheme = HTTPBearer(auto_error=False)


def create_token(sub: str) -> str:
    settings = get_settings()
    payload = {
        "sub": sub,
        "exp": dt.datetime.utcnow() + dt.timedelta(minutes=settings.platform.auth.token_ttl_minutes),
    }
    return jwt.encode(payload, settings.platform.auth.jwt_secret, algorithm=settings.platform.auth.jwt_algorithm)


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)) -> str:
    settings = get_settings()
    if not settings.platform.auth.enabled:
        return "anonymous"
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.platform.auth.jwt_secret, algorithms=[settings.platform.auth.jwt_algorithm])
        return payload.get("sub") or "anonymous"
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
