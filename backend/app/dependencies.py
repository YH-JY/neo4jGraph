from __future__ import annotations

from fastapi import Request

from app.services.import_service import ImportService


def get_import_service(request: Request) -> ImportService:
    return request.app.state.import_service  # type: ignore[attr-defined]
