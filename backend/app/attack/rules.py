from __future__ import annotations

import hashlib
from typing import List, Tuple

from app.schemas.graph import GraphEdge, GraphNode
from app.schemas.kube import KubeSnapshot


def _attack_node_id(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()[:12]


class AttackAnalyzer:
    def detect(self, snapshot: KubeSnapshot) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        rbac_nodes, rbac_edges = self._detect_rbac(snapshot)
        nodes.extend(rbac_nodes)
        edges.extend(rbac_edges)
        escape_nodes, escape_edges = self._detect_container_escape(snapshot)
        nodes.extend(escape_nodes)
        edges.extend(escape_edges)
        return nodes, edges

    def _detect_rbac(self, snapshot: KubeSnapshot) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        high_priv_roles = {role.metadata.get("name") for role in snapshot.cluster_roles if any("*" in r.get("verbs", []) for r in role.dict().get("rules", []))}
        for binding in list(snapshot.role_bindings) + list(snapshot.cluster_role_bindings):
            role_ref = binding.dict().get("roleRef") or {}
            role_name = role_ref.get("name")
            if role_name in (high_priv_roles or {"cluster-admin"}):
                subjects = binding.dict().get("subjects", [])
                for subject in subjects:
                    node_id = _attack_node_id(f"rbac-{binding.metadata.get('name')}-{subject.get('name')}")
                    attack_node = GraphNode(
                        label="AttackTechnique",
                        key=node_id,
                        properties={
                            "technique": "RBAC_Escalation",
                            "severity": "high",
                            "description": f"{subject.get('name')} 绑定高危角色 {role_name}",
                            "binding": binding.metadata.get("name"),
                        },
                    )
                    nodes.append(attack_node)
                    edges.append(
                        GraphEdge(
                            source=subject.get("uid") or subject.get("name"),
                            target=node_id,
                            relation="POSSIBLE_ATTACK_PATH",
                            properties={"reason": "High privilege binding"},
                        )
                    )
        return nodes, edges

    def _detect_container_escape(self, snapshot: KubeSnapshot) -> Tuple[List[GraphNode], List[GraphEdge]]:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        for pod in snapshot.pods:
            spec = pod.spec or {}
            volumes = spec.get("volumes", [])
            for container in spec.get("containers", []):
                security = container.get("securityContext", {})
                privileged = security.get("privileged")
                mounts = container.get("volumeMounts", [])
                risky_mount = next((m for m in mounts if m.get("mountPath") == "/host"), None)
                hostpath = any("hostPath" in volume for volume in volumes)
                if privileged or (risky_mount and hostpath):
                    node_id = _attack_node_id(f"escape-{pod.metadata['uid']}-{container['name']}")
                    nodes.append(
                        GraphNode(
                            label="AttackTechnique",
                            key=node_id,
                            properties={
                                "technique": "Container_Escape",
                                "severity": "medium" if not privileged else "critical",
                                "description": f"Pod {pod.metadata.get('name')} 可能具备容器逃逸条件",
                            },
                        )
                    )
                    edges.append(
                        GraphEdge(
                            source=pod.metadata.get("uid"),
                            target=node_id,
                            relation="POSSIBLE_ATTACK_PATH",
                            properties={"container": container.get("name")},
                        )
                    )
        return nodes, edges
