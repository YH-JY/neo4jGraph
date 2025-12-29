from __future__ import annotations

from fastapi import APIRouter

from app.core.settings import get_settings, refresh_settings
from app.schemas.api import ConfigureRequest, ConfigureResponse

router = APIRouter(prefix="/api", tags=["config"])


@router.get("/config", response_model=ConfigureResponse)
def read_config() -> ConfigureResponse:
    settings = get_settings()
    return ConfigureResponse(message="ok", applied=settings.model_dump())


@router.post("/configure", response_model=ConfigureResponse)
def update_config(payload: ConfigureRequest) -> ConfigureResponse:
    merged = refresh_settings(payload.model_dump(exclude_none=True))
    return ConfigureResponse(message="updated", applied=merged.model_dump())
