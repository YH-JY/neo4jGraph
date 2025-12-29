from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.schemas.api import ExportRequest
from app.services.export_service import export_graph

router = APIRouter(prefix="/api", tags=["export"])


@router.post("/export")
def export_graph_route(payload: ExportRequest) -> StreamingResponse:
    filename, content, media_type = export_graph(payload.format, payload.cypher)
    return StreamingResponse(iter([content]), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/export")
def export_graph_get(fmt: str = Query("json"), cypher: str | None = None) -> StreamingResponse:
    filename, content, media_type = export_graph(fmt, cypher)
    return StreamingResponse(iter([content]), media_type=media_type, headers={"Content-Disposition": f"attachment; filename={filename}"})
