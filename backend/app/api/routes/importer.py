from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.security import verify_token
from app.dependencies import get_import_service
from app.schemas.api import ImportResponse
from app.services.import_service import ImportService

router = APIRouter(prefix="/api/import", tags=["import"])


@router.post("/k8s", response_model=ImportResponse)
def import_k8s(
    mock: bool = Query(False, description="使用内置示例数据"),
    _: str = Depends(verify_token),
    service: ImportService = Depends(get_import_service),
) -> ImportResponse:
    nodes, edges = service.import_cluster(use_mock=mock)
    return ImportResponse(message="imported", nodes=nodes, edges=edges)
