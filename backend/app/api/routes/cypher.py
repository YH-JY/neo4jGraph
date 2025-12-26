from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.security import verify_token
from app.schemas.api import CypherGraph, CypherRequest
from app.services.cypher_executor import execute_with_limits
from app.services.graph_converter import records_to_graph

router = APIRouter(prefix="/api", tags=["cypher"])


@router.post("/cypher", response_model=CypherGraph)
def run_cypher(payload: CypherRequest, _: str = Depends(verify_token)) -> CypherGraph:
    data = execute_with_limits(payload.query, payload.params)
    nodes, edges = records_to_graph(data)
    return CypherGraph(nodes=nodes, edges=edges, raw=data)
