from __future__ import annotations

from typing import Dict, Iterable, List

from neo4j.graph import Node as Neo4jNode
from neo4j.graph import Relationship as Neo4jRelationship

from app.schemas.graph import GraphEdge, GraphNode


def records_to_graph(records: Iterable[dict]) -> tuple[List[GraphNode], List[GraphEdge]]:
    node_map: Dict[str, GraphNode] = {}
    edges: List[GraphEdge] = []

    for record in records:
        for value in record.values():
            if isinstance(value, Neo4jNode):
                key = value.get("key") or str(value.id)
                label = next(iter(value.labels), "Node")
                node_map[key] = GraphNode(label=label, key=key, properties=dict(value))
            elif isinstance(value, Neo4jRelationship):
                source = value.start_node.get("key") or str(value.start_node.id)
                target = value.end_node.get("key") or str(value.end_node.id)
                edges.append(
                    GraphEdge(
                        source=source,
                        target=target,
                        relation=value.type,
                        properties=dict(value),
                    )
                )
            elif isinstance(value, list):
                nested_nodes, nested_edges = records_to_graph([{"value": item} for item in value])
                for node in nested_nodes:
                    node_map[node.key] = node
                edges.extend(nested_edges)
    return list(node_map.values()), edges
