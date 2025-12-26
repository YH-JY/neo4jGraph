from __future__ import annotations

from .types import CollectorResult


def sample_cluster_state() -> CollectorResult:
    return CollectorResult(
        pods=[
            {
                "metadata": {"name": "api", "namespace": "default", "uid": "pod-1", "labels": {"app": "api"}},
                "spec": {
                    "nodeName": "worker-1",
                    "serviceAccountName": "api-sa",
                    "containers": [
                        {
                            "name": "api",
                            "image": "registry.local/api:1.0",
                            "securityContext": {"privileged": False},
                            "volumeMounts": [
                                {"name": "config", "mountPath": "/etc/config"}
                            ],
                        }
                    ],
                    "volumes": [
                        {"name": "config", "configMap": {"name": "api-config"}}
                    ],
                },
                "status": {"phase": "Running"},
            },
            {
                "metadata": {
                    "name": "privileged-debug",
                    "namespace": "security",
                    "uid": "pod-escape",
                },
                "spec": {
                    "nodeName": "worker-2",
                    "serviceAccountName": "debug-sa",
                    "containers": [
                        {
                            "name": "debug",
                            "image": "alpine",
                            "securityContext": {"privileged": True},
                            "volumeMounts": [
                                {"name": "host-root", "mountPath": "/host"}
                            ],
                        }
                    ],
                    "volumes": [
                        {"name": "host-root", "hostPath": {"path": "/"}},
                    ],
                },
                "status": {"phase": "Running"},
            },
        ],
        nodes=[
            {"metadata": {"name": "worker-1"}, "status": {"nodeInfo": {"kubeletVersion": "1.28"}}},
            {"metadata": {"name": "worker-2"}, "status": {"nodeInfo": {"kubeletVersion": "1.28"}}},
        ],
        service_accounts=[
            {"metadata": {"name": "api-sa", "namespace": "default", "uid": "sa-api"}},
            {"metadata": {"name": "debug-sa", "namespace": "security", "uid": "sa-debug"}},
        ],
        roles=[
            {
                "metadata": {"name": "api-reader", "namespace": "default"},
                "rules": [
                    {"verbs": ["get", "list"], "resources": ["pods"]}
                ],
            }
        ],
        cluster_roles=[
            {
                "metadata": {"name": "cluster-admin"},
                "rules": [
                    {"verbs": ["*"]}
                ],
            }
        ],
        role_bindings=[
            {
                "metadata": {"name": "debug-admin", "namespace": "security"},
                "roleRef": {"kind": "ClusterRole", "name": "cluster-admin"},
                "subjects": [
                    {"kind": "ServiceAccount", "name": "debug-sa", "namespace": "security"}
                ],
            }
        ],
        cluster_role_bindings=[],
        secrets=[
            {
                "metadata": {"name": "api-secret", "namespace": "default"},
                "type": "Opaque",
            }
        ],
        configmaps=[
            {"metadata": {"name": "api-config", "namespace": "default"}}
        ],
        services=[
            {
                "metadata": {"name": "api-svc", "namespace": "default"},
                "spec": {"selector": {"app": "api"}, "ports": [{"port": 80}]},
            }
        ],
        ingresses=[],
    )
