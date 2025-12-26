from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException, status

from app.core.security import create_token
from app.schemas.api import TokenRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def login(payload: TokenRequest) -> TokenResponse:
    username = os.getenv("DEFAULT_ADMIN_USER", "admin")
    password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
    if payload.username != username or payload.password != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token(payload.username)
    return TokenResponse(access_token=token)
