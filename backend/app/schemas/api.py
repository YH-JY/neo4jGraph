from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .graph import GraphEdge, GraphNode


class ConfigureRequest(BaseModel):
    neo4j: Optional[Dict[str, Any]] = None
    kubernetes: Optional[Dict[str, Any]] = None
    platform: Optional[Dict[str, Any]] = None


class ConfigureResponse(BaseModel):
    message: str
    applied: Dict[str, Any]


class CypherRequest(BaseModel):
    query: str
    params: Dict[str, Any] = Field(default_factory=dict)
    limit: Optional[int] = None


class CypherGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    raw: List[Dict[str, Any]]


class ImportResponse(BaseModel):
    nodes: int
    edges: int
    message: str


class PresetQuery(BaseModel):
    id: str
    label: str
    query: str
    description: str


class ExportRequest(BaseModel):
    format: str = Field(default="png")
    cypher: Optional[str] = None


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
