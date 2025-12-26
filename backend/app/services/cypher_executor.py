from __future__ import annotations

import time
from typing import Any, Dict, List

from fastapi import HTTPException, status

from app.core.settings import get_settings
from .neo4j_service import run_cypher


FORBIDDEN_KEYWORDS = {"CALL dbms.shutdown"}


def execute_with_limits(query: str, parameters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    settings = get_settings()
    normalized = query.strip()
    if len(normalized) > 20000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query too long")

    lowered = normalized.lower()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword.lower() in lowered:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden Cypher keyword")

    start = time.monotonic()
    data = run_cypher(normalized, parameters)
    duration_ms = (time.monotonic() - start) * 1000
    if duration_ms > settings.platform.max_cypher_time_ms:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Cypher execution timeout")

    if len(data) > settings.platform.max_cypher_rows:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Result too large")
    return data
