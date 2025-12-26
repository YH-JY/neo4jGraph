from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.schemas.kube import KubeResource, KubeSnapshot


def _as_resource(payload: Dict[str, Any], kind: str) -> KubeResource:
    data = {**payload}
    data.setdefault("kind", kind)
    return KubeResource.model_validate(data)


class CollectorResult(BaseModel):
    pods: List[Dict[str, Any]] = Field(default_factory=list)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    service_accounts: List[Dict[str, Any]] = Field(default_factory=list)
    roles: List[Dict[str, Any]] = Field(default_factory=list)
    cluster_roles: List[Dict[str, Any]] = Field(default_factory=list)
    role_bindings: List[Dict[str, Any]] = Field(default_factory=list)
    cluster_role_bindings: List[Dict[str, Any]] = Field(default_factory=list)
    secrets: List[Dict[str, Any]] = Field(default_factory=list)
    configmaps: List[Dict[str, Any]] = Field(default_factory=list)
    services: List[Dict[str, Any]] = Field(default_factory=list)
    ingresses: List[Dict[str, Any]] = Field(default_factory=list)

    def to_snapshot(self) -> KubeSnapshot:
        return KubeSnapshot(
            pods=[_as_resource(pod, "Pod") for pod in self.pods],
            nodes=[_as_resource(node, "Node") for node in self.nodes],
            service_accounts=[_as_resource(sa, "ServiceAccount") for sa in self.service_accounts],
            roles=[_as_resource(role, "Role") for role in self.roles],
            cluster_roles=[_as_resource(role, "ClusterRole") for role in self.cluster_roles],
            role_bindings=[_as_resource(rb, "RoleBinding") for rb in self.role_bindings],
            cluster_role_bindings=[_as_resource(rb, "ClusterRoleBinding") for rb in self.cluster_role_bindings],
            secrets=[_as_resource(sec, "Secret") for sec in self.secrets],
            configmaps=[_as_resource(cm, "ConfigMap") for cm in self.configmaps],
            services=[_as_resource(svc, "Service") for svc in self.services],
            ingresses=[_as_resource(ing, "Ingress") for ing in self.ingresses],
        )
