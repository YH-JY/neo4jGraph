from app.attack.rules import AttackAnalyzer
from app.schemas.kube import KubeResource, KubeSnapshot


def make_pod(uid: str, privileged: bool = False):
    return KubeResource(
        kind="Pod",
        metadata={"name": uid, "namespace": "default", "uid": uid},
        spec={
            "nodeName": "node-1",
            "serviceAccountName": "sa-1",
            "containers": [
                {
                    "name": "c1",
                    "image": "test",
                    "securityContext": {"privileged": privileged},
                    "volumeMounts": [],
                }
            ],
            "volumes": [],
        },
    )


def test_attack_analyzer_detects_container_escape():
    snapshot = KubeSnapshot(pods=[make_pod("pod-1", privileged=True)])
    analyzer = AttackAnalyzer()
    nodes, edges = analyzer.detect(snapshot)
    assert any(n.properties["technique"] == "Container_Escape" for n in nodes)
    assert edges


def test_attack_analyzer_detects_rbac():
    snapshot = KubeSnapshot(
        cluster_roles=[
            KubeResource(kind="ClusterRole", metadata={"name": "cluster-admin"}, rules=[{"verbs": ["*"]}])
        ],
        role_bindings=[
            KubeResource(
                kind="RoleBinding",
                metadata={"name": "rb", "namespace": "default"},
                roleRef={"kind": "ClusterRole", "name": "cluster-admin"},
                subjects=[{"kind": "ServiceAccount", "name": "sa", "namespace": "default"}],
            )
        ],
    )
    analyzer = AttackAnalyzer()
    nodes, _ = analyzer.detect(snapshot)
    assert any(n.properties["technique"] == "RBAC_Escalation" for n in nodes)
