from __future__ import annotations

import re
import threading
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List

from neo4j import GraphDatabase, basic_auth
from neo4j.work.simple import Session
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.logging import get_logger
from app.core.settings import get_settings

logger = get_logger("neo4j")
_driver = None
_driver_lock = threading.Lock()

DESTRUCTIVE_PATTERN = re.compile(r"\b(DETACH\s+DELETE|DROP\s+|REMOVE\s+)\b", re.IGNORECASE)


def get_driver():
    global _driver
    settings = get_settings()
    if _driver:
        return _driver
    with _driver_lock:
        if _driver:
            return _driver
        logger.info("Initializing Neo4j driver", uri=settings.neo4j.uri)
        _driver = GraphDatabase.driver(
            settings.neo4j.uri,
            auth=basic_auth(settings.neo4j.user, settings.neo4j.password),
            max_connection_pool_size=settings.neo4j.max_connection_pool_size,
            encrypted=settings.neo4j.encrypted,
        )
    return _driver


@contextmanager
def get_session() -> Iterable[Session]:
    driver = get_driver()
    settings = get_settings()
    session = driver.session(database=settings.neo4j.database)
    try:
        yield session
    finally:
        session.close()


def guard_cypher(query: str) -> None:
    settings = get_settings()
    if settings.security.allow_destructive_cypher:
        return
    if DESTRUCTIVE_PATTERN.search(query):
        raise ValueError("Destructive Cypher is not allowed")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def run_cypher(query: str, parameters: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    guard_cypher(query)
    with get_session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def run_write(statements: List[Dict[str, Any]]) -> None:
    def tx_work(tx):
        for stmt in statements:
            guard_cypher(stmt["query"])
            tx.run(stmt["query"], stmt.get("params", {}))

    with get_session() as session:
        session.execute_write(tx_work)
