from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import verify_token
from app.core.settings import get_settings, refresh_settings
from app.schemas.api import ConfigureRequest, ConfigureResponse

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config", response_model=ConfigureResponse)
def read_config(_: str = Depends(verify_token)) -> ConfigureResponse:
    settings = get_settings()
    return ConfigureResponse(message="ok", applied=settings.model_dump())


@router.post("/configure", response_model=ConfigureResponse)
def update_config(payload: ConfigureRequest, _: str = Depends(verify_token)) -> ConfigureResponse:
    merged = refresh_settings(payload.model_dump(exclude_none=True))
    return ConfigureResponse(message="updated", applied=merged.model_dump())
