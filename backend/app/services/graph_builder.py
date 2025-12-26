from __future__ import annotations

from collections import OrderedDict
from typing import Dict, List, Tuple

from app.attack.rules import AttackAnalyzer
from app.schemas.graph import GraphEdge, GraphNode
from app.schemas.kube import KubeResource, KubeSnapshot


class GraphBuilder:
    def __init__(self) -> None:
        self.analyzer = AttackAnalyzer()

    def build(self, snapshot: KubeSnapshot) -> Tuple[List[GraphNode], List[GraphEdge]]:
        node_map: Dict[str, GraphNode] = OrderedDict()
        edges: List[GraphEdge] = []

        self._map_nodes(snapshot, node_map)
        edges.extend(self._map_relationships(snapshot))

        attack_nodes, attack_edges = self.analyzer.detect(snapshot)
        for node in attack_nodes:
            self._add_node(node_map, node)
        edges.extend(attack_edges)

        return list(node_map.values()), edges

    def build_statements(self, snapshot: KubeSnapshot) -> List[Dict[str, Dict]]:
        nodes, edges = self.build(snapshot)
        return self.to_statements(nodes, edges)

    def to_statements(self, nodes: List[GraphNode], edges: List[GraphEdge]) -> List[Dict[str, Dict]]:
        statements: List[Dict[str, Dict]] = []
        for node in nodes:
            statements.append(
                {
                    "query": f"MERGE (n:{node.label} {{key: $key}}) SET n += $props",
                    "params": {"key": node.key, "props": {**node.properties, "key": node.key}},
                }
            )
        for edge in edges:
            statements.append(
                {
                    "query": f"MATCH (a {{key: $source}}) MATCH (b {{key: $target}}) MERGE (a)-[r:{edge.relation}]->(b) SET r += $props",
                    "params": {
                        "source": edge.source,
                        "target": edge.target,
                        "props": edge.properties,
                    },
                }
            )
        return statements

    def _map_nodes(self, snapshot: KubeSnapshot, node_map: Dict[str, GraphNode]) -> None:
        for pod in snapshot.pods:
            key = _pod_key(pod)
            props = {
                "name": pod.metadata.get("name"),
                "namespace": pod.metadata.get("namespace"),
                "labels": pod.metadata.get("labels", {}),
                "phase": (pod.status or {}).get("phase"),
                "node": (pod.spec or {}).get("nodeName"),
            }
            self._add_node(node_map, GraphNode(label="Pod", key=key, properties=props))
            for container in (pod.spec or {}).get("containers", []):
                c_key = f"container:{pod.metadata.get('namespace')}:{pod.metadata.get('name')}:{container['name']}"
                c_props = {
                    "name": container.get("name"),
                    "image": container.get("image"),
                    "pod": pod.metadata.get("name"),
                }
                self._add_node(node_map, GraphNode(label="Container", key=c_key, properties=c_props))

        for node in snapshot.nodes:
            key = node.metadata.get("uid") or f"node:{node.metadata.get('name')}"
            props = {
                "name": node.metadata.get("name"),
                "labels": node.metadata.get("labels", {}),
                "kubeletVersion": (node.status or {}).get("nodeInfo", {}).get("kubeletVersion"),
            }
            self._add_node(node_map, GraphNode(label="Node", key=key, properties=props))

        for sa in snapshot.service_accounts:
            key = _service_account_key(sa)
            props = {
                "name": sa.metadata.get("name"),
                "namespace": sa.metadata.get("namespace"),
            }
            self._add_node(node_map, GraphNode(label="ServiceAccount", key=key, properties=props))

        for role in snapshot.roles:
            key = f"role:{role.metadata.get('namespace')}:{role.metadata.get('name')}"
            self._add_node(
                node_map,
                GraphNode(
                    label="Role",
                    key=key,
                    properties={
                        "name": role.metadata.get("name"),
                        "namespace": role.metadata.get("namespace"),
                        "rules": role.dict().get("rules", []),
                        "fqname": key,
                    },
                ),
            )

        for role in snapshot.cluster_roles:
            key = f"clusterrole:{role.metadata.get('name')}"
            self._add_node(
                node_map,
                GraphNode(
                    label="ClusterRole",
                    key=key,
                    properties={"name": role.metadata.get("name"), "rules": role.dict().get("rules", [])},
                ),
            )

        for binding in snapshot.role_bindings + snapshot.cluster_role_bindings:
            key = binding.metadata.get("uid") or f"binding:{binding.metadata.get('namespace')}:{binding.metadata.get('name')}"
            self._add_node(
                node_map,
                GraphNode(
                    label="Binding",
                    key=key,
                    properties={
                        "name": binding.metadata.get("name"),
                        "namespace": binding.metadata.get("namespace"),
                        "roleRef": binding.dict().get("roleRef", {}),
                    },
                ),
            )

        for secret in snapshot.secrets:
            key = f"secret:{secret.metadata.get('namespace')}:{secret.metadata.get('name')}"
            props = {
                "name": secret.metadata.get("name"),
                "namespace": secret.metadata.get("namespace"),
                "type": secret.dict().get("type"),
            }
            self._add_node(node_map, GraphNode(label="Secret", key=key, properties=props))

        for configmap in snapshot.configmaps:
            key = f"configmap:{configmap.metadata.get('namespace')}:{configmap.metadata.get('name')}"
            props = {
                "name": configmap.metadata.get("name"),
                "namespace": configmap.metadata.get("namespace"),
            }
            self._add_node(node_map, GraphNode(label="ConfigMap", key=key, properties=props))

        for service in snapshot.services:
            key = f"service:{service.metadata.get('namespace')}:{service.metadata.get('name')}"
            props = {
                "name": service.metadata.get("name"),
                "namespace": service.metadata.get("namespace"),
                "ports": (service.spec or {}).get("ports", []),
                "selector": (service.spec or {}).get("selector", {}),
            }
            self._add_node(node_map, GraphNode(label="Service", key=key, properties=props))

        for ingress in snapshot.ingresses:
            key = f"ingress:{ingress.metadata.get('namespace')}:{ingress.metadata.get('name')}"
            props = {
                "name": ingress.metadata.get("name"),
                "namespace": ingress.metadata.get("namespace"),
                "rules": (ingress.spec or {}).get("rules", []),
            }
            self._add_node(node_map, GraphNode(label="Ingress", key=key, properties=props))

    def _map_relationships(self, snapshot: KubeSnapshot) -> List[GraphEdge]:
        edges: List[GraphEdge] = []
        node_key_cache = {
            node.metadata.get("name"): node.metadata.get("uid") or f"node:{node.metadata.get('name')}"
            for node in snapshot.nodes
        }
        for pod in snapshot.pods:
            pod_key = _pod_key(pod)
            node_name = (pod.spec or {}).get("nodeName")
            if node_name and node_name in node_key_cache:
                edges.append(GraphEdge(source=pod_key, target=node_key_cache[node_name], relation="RUNS_ON"))
            sa_name = (pod.spec or {}).get("serviceAccountName")
            if sa_name:
                sa_key = _service_account_key(
                    KubeResource(
                        kind="ServiceAccount",
                        metadata={
                            "name": sa_name,
                            "namespace": pod.metadata.get("namespace"),
                        },
                    )
                )
                edges.append(
                    GraphEdge(
                        source=pod_key,
                        target=sa_key,
                        relation="USES_SERVICEACCOUNT",
                    )
                )
            for container in (pod.spec or {}).get("containers", []):
                container_key = f"container:{pod.metadata.get('namespace')}:{pod.metadata.get('name')}:{container['name']}"
                edges.append(
                    GraphEdge(
                        source=pod_key,
                        target=container_key,
                        relation="CONTAINS",
                    )
                )
            for volume in (pod.spec or {}).get("volumes", []):
                if volume.get("secret"):
                    secret_name = volume["secret"].get("secretName") or volume["secret"].get("name")
                    if secret_name:
                        secret_key = f"secret:{pod.metadata.get('namespace')}:{secret_name}"
                        edges.append(
                            GraphEdge(
                                source=pod_key,
                                target=secret_key,
                                relation="HAS_SECRET",
                                properties={"volume": volume.get("name")},
                            )
                        )
        for binding in snapshot.role_bindings + snapshot.cluster_role_bindings:
            binding_key = binding.metadata.get("uid") or f"binding:{binding.metadata.get('namespace')}:{binding.metadata.get('name')}"
            role_ref = binding.dict().get("roleRef", {})
            if role_ref:
                if role_ref.get("kind") == "ClusterRole":
                    role_key = f"clusterrole:{role_ref.get('name')}"
                else:
                    role_key = f"role:{binding.metadata.get('namespace')}:{role_ref.get('name')}"
                edges.append(GraphEdge(source=binding_key, target=role_key, relation="GRANTS"))
            for subject in binding.dict().get("subjects", []):
                if subject.get("kind") == "ServiceAccount":
                    sa_key = _service_account_key(
                        KubeResource(
                            kind="ServiceAccount",
                            metadata={
                                "name": subject.get("name"),
                                "namespace": subject.get("namespace", binding.metadata.get("namespace")),
                                "uid": subject.get("uid"),
                            },
                        )
                    )
                    edges.append(
                        GraphEdge(
                            source=binding_key,
                            target=sa_key,
                            relation="BOUND_TO",
                        )
                    )
                    if role_ref:
                        if role_ref.get("kind") == "ClusterRole":
                            role_key = f"clusterrole:{role_ref.get('name')}"
                        else:
                            role_key = f"role:{binding.metadata.get('namespace')}:{role_ref.get('name')}"
                        edges.append(
                            GraphEdge(
                                source=sa_key,
                                target=role_key,
                                relation="CAN_ACCESS",
                                properties={"binding": binding.metadata.get("name")},
                            )
                        )
        return edges

    def _add_node(self, node_map: Dict[str, GraphNode], node: GraphNode) -> None:
        existing = node_map.get(node.key)
        if existing:
            existing.properties.update(node.properties)
        else:
            node_map[node.key] = node


def _pod_key(pod: KubeResource) -> str:
    return pod.metadata.get("uid") or f"pod:{pod.metadata.get('namespace')}:{pod.metadata.get('name')}"


def _service_account_key(sa: KubeResource) -> str:
    uid = sa.metadata.get("uid")
    if uid:
        return uid
    return f"sa:{sa.metadata.get('namespace')}:{sa.metadata.get('name')}"
