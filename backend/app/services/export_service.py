from __future__ import annotations

import io
import json
from datetime import datetime

import matplotlib
import networkx as nx

from app.services.cypher_executor import execute_with_limits
from app.services.graph_converter import records_to_graph

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def export_graph(fmt: str, query: str | None = None):
    cypher = query or "MATCH (n)-[r]->(m) RETURN n,r,m"
    records = execute_with_limits(cypher)
    nodes, edges = records_to_graph(records)

    if fmt.lower() == "json":
        payload = json.dumps({"nodes": [n.model_dump() for n in nodes], "edges": [e.model_dump() for e in edges]}, ensure_ascii=False)
        return "graph.json", payload.encode("utf-8"), "application/json"
    if fmt.lower() == "cypher":
        return "query.cypher", cypher.encode("utf-8"), "application/cypher"

    graph = nx.DiGraph()
    for node in nodes:
        graph.add_node(node.key, label=node.properties.get("name") or node.label)
    for edge in edges:
        graph.add_edge(edge.source, edge.target, relation=edge.relation)

    pos = nx.spring_layout(graph, seed=42)
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_size=600, node_color="#5B8FF9", alpha=0.8)
    nx.draw_networkx_edges(graph, pos, ax=ax, arrowstyle="->", arrowsize=10, edge_color="#999999")
    labels = {node: graph.nodes[node].get("label", node) for node in graph.nodes}
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=8)
    ax.axis("off")
    buffer = io.BytesIO()
    image_format = "png" if fmt.lower() == "png" else "svg"
    fig.savefig(buffer, format=image_format, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    media_type = "image/png" if image_format == "png" else "image/svg+xml"
    filename = f"graph-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.{image_format}"
    return filename, buffer.read(), media_type
