from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import verify_token
from app.services.neo4j_service import run_cypher

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/node/{key}")
def get_node(key: str, _: str = Depends(verify_token)) -> dict:
    data = run_cypher("MATCH (n {key: $key}) OPTIONAL MATCH (n)-[r]-(m) RETURN n, collect({rel: type(r), node: m, relProps: properties(r)}) as relations", {"key": key})
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found")
    return data[0]


@router.get("/edge/{relation_id}")
def get_edge(relation_id: str, _: str = Depends(verify_token)) -> dict:
    data = run_cypher("MATCH ()-[r]->() WHERE elementId(r) = $id RETURN r", {"id": relation_id})
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found")
    return data[0]
