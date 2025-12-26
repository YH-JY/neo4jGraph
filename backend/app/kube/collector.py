from __future__ import annotations

from typing import List

from kubernetes import client, config
from kubernetes.client import ApiClient

from app.core.logging import get_logger
from app.core.settings import get_settings

from .sample_data import sample_cluster_state
from .types import CollectorResult

logger = get_logger("collector")


class KubeCollector:
    def __init__(self) -> None:
        self.settings = get_settings().kubernetes
        self._api_client: ApiClient | None = None
        self._loaded = False

    def _ensure_client(self) -> None:
        if self._loaded:
            return
        config.load_kube_config(config_file=self.settings.kubeconfig_path)
        self._api_client = ApiClient()
        self._loaded = True
        logger.info("Loaded kubeconfig", path=self.settings.kubeconfig_path)

    def _serialize(self, items: List) -> List[dict]:
        if not self._api_client:
            raise RuntimeError("API client not initialized")
        return [self._api_client.sanitize_for_serialization(item) for item in items]

    def fetch(self, use_mock: bool = False) -> CollectorResult:
        if use_mock:
            logger.warning("Using mock Kubernetes data")
            return sample_cluster_state()
        try:
            self._ensure_client()
            core = client.CoreV1Api(self._api_client)
            rbac = client.RbacAuthorizationV1Api(self._api_client)
            networking = client.NetworkingV1Api(self._api_client)

            pods = self._serialize(core.list_pod_for_all_namespaces().items)
            nodes = self._serialize(core.list_node().items)
            sas = self._serialize(core.list_service_account_for_all_namespaces().items)
            roles = self._serialize(rbac.list_role_for_all_namespaces().items)
            crs = self._serialize(rbac.list_cluster_role().items)
            rbs = self._serialize(rbac.list_role_binding_for_all_namespaces().items)
            crbs = self._serialize(rbac.list_cluster_role_binding().items)
            secrets = self._serialize(core.list_secret_for_all_namespaces().items)
            configmaps = self._serialize(core.list_config_map_for_all_namespaces().items)
            services = self._serialize(core.list_service_for_all_namespaces().items)
            ingresses = self._serialize(networking.list_ingress_for_all_namespaces().items)

            return CollectorResult(
                pods=pods,
                nodes=nodes,
                service_accounts=sas,
                roles=roles,
                cluster_roles=crs,
                role_bindings=rbs,
                cluster_role_bindings=crbs,
                secrets=secrets,
                configmaps=configmaps,
                services=services,
                ingresses=ingresses,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to collect k8s data, fallback to mock", error=str(exc))
            return sample_cluster_state()
