from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class KubeResource(BaseModel):
    model_config = ConfigDict(extra="allow")

    kind: str
    metadata: dict
    spec: dict | None = None
    status: dict | None = None


class KubeSnapshot(BaseModel):
    pods: List[KubeResource] = Field(default_factory=list)
    nodes: List[KubeResource] = Field(default_factory=list)
    service_accounts: List[KubeResource] = Field(default_factory=list)
    roles: List[KubeResource] = Field(default_factory=list)
    cluster_roles: List[KubeResource] = Field(default_factory=list)
    role_bindings: List[KubeResource] = Field(default_factory=list)
    cluster_role_bindings: List[KubeResource] = Field(default_factory=list)
    secrets: List[KubeResource] = Field(default_factory=list)
    configmaps: List[KubeResource] = Field(default_factory=list)
    services: List[KubeResource] = Field(default_factory=list)
    ingresses: List[KubeResource] = Field(default_factory=list)
