from app.schemas.kube import KubeResource, KubeSnapshot
from app.services.graph_builder import GraphBuilder


def test_graph_builder_outputs_statements():
    snapshot = KubeSnapshot(
        pods=[
            KubeResource(
                kind="Pod",
                metadata={"name": "api", "namespace": "default", "uid": "pod-1"},
                spec={"nodeName": "node-1", "serviceAccountName": "sa", "containers": []},
            )
        ],
        nodes=[KubeResource(kind="Node", metadata={"name": "node-1", "uid": "node-1"})],
        service_accounts=[KubeResource(kind="ServiceAccount", metadata={"name": "sa", "namespace": "default", "uid": "sa-1"})],
    )
    builder = GraphBuilder()
    statements = builder.build_statements(snapshot)
    assert any("Pod" in stmt["query"] for stmt in statements)
    assert any("RUNS_ON" in stmt["query"] for stmt in statements)
