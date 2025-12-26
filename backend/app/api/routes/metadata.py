from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import verify_token
from app.schemas.api import PresetQuery
from app.services.preset_queries import PRESET_QUERIES

router = APIRouter(prefix="/api", tags=["metadata"])


@router.get("/preset-queries", response_model=list[PresetQuery])
def preset_queries(_: str = Depends(verify_token)) -> list[PresetQuery]:
    return PRESET_QUERIES
