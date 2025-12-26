from __future__ import annotations

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    label: str
    key: str
    properties: dict = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    properties: dict = Field(default_factory=dict)
