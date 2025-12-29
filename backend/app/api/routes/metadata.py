from __future__ import annotations

from fastapi import APIRouter

from app.schemas.api import PresetQuery
from app.services.preset_queries import PRESET_QUERIES

router = APIRouter(prefix="/api", tags=["metadata"])


@router.get("/preset-queries", response_model=list[PresetQuery])
def preset_queries() -> list[PresetQuery]:
    return PRESET_QUERIES
