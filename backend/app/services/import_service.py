from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.logging import get_logger
from app.core.settings import get_settings
from app.kube.collector import KubeCollector
from app.kube.types import CollectorResult
from app.schemas.kube import KubeSnapshot

from .graph_builder import GraphBuilder
from .neo4j_service import run_write

logger = get_logger("importer")


class ImportService:
    def __init__(self) -> None:
        self.collector = KubeCollector()
        self.builder = GraphBuilder()
        self.scheduler: BackgroundScheduler | None = None

    def import_cluster(self, use_mock: bool = False) -> tuple[int, int]:
        result: CollectorResult = self.collector.fetch(use_mock=use_mock)
        snapshot: KubeSnapshot = result.to_snapshot()
        nodes, edges = self.builder.build(snapshot)
        statements = self.builder.to_statements(nodes, edges)
        run_write(statements)
        return len(nodes), len(edges)

    def start_scheduler(self) -> None:
        settings = get_settings()
        if not settings.sync.enabled:
            return
        if self.scheduler:
            return
        trigger = CronTrigger.from_crontab(settings.sync.schedule)
        self.scheduler = BackgroundScheduler(timezone="UTC")
        self.scheduler.add_job(self.import_cluster, trigger=trigger, id="k8s-sync", replace_existing=True)
        self.scheduler.start()
        logger.info("Sync scheduler started", schedule=settings.sync.schedule)

    def shutdown(self) -> None:
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            self.scheduler = None
