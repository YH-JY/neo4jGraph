from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from pydantic import BaseModel, Field


class AuthSettings(BaseModel):
    enabled: bool = True
    jwt_secret: str = Field(default_factory=lambda: os.getenv("JWT_SECRET", "please_change_me"))
    jwt_algorithm: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    token_ttl_minutes: int = Field(default=int(os.getenv("JWT_TTL_MINUTES", 60)))


class PlatformSettings(BaseModel):
    api_host: str = Field(default=os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = Field(default=int(os.getenv("API_PORT", 8080)))
    frontend_url: str = Field(default=os.getenv("FRONTEND_URL", "http://localhost:5173"))
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    max_cypher_rows: int = Field(default=int(os.getenv("MAX_CYPHER_ROWS", 10000)))
    max_cypher_time_ms: int = Field(default=int(os.getenv("MAX_CYPHER_TIME_MS", 5000)))
    allow_cors_origins: list[str] = Field(default_factory=list)
    auth: AuthSettings = Field(default_factory=AuthSettings)


class Neo4jSettings(BaseModel):
    uri: str = Field(default=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"))
    user: str = Field(default=os.getenv("NEO4J_USER", "neo4j"))
    password: str = Field(default=os.getenv("NEO4J_PASSWORD", "neo4j"))
    database: str = Field(default=os.getenv("NEO4J_DATABASE", "neo4j"))
    max_connection_pool_size: int = Field(default=int(os.getenv("NEO4J_POOL_SIZE", 50)))
    encrypted: bool = Field(default=os.getenv("NEO4J_ENCRYPTED", "false").lower() == "true")


class KubernetesSettings(BaseModel):
    kubeconfig_path: str = Field(
        default=os.getenv("KUBECONFIG_PATH", str(Path.home() / ".kube/config"))
    )
    verify_ssl: bool = Field(default=os.getenv("KUBE_VERIFY_SSL", "true").lower() == "true")
    request_timeout_seconds: int = Field(
        default=int(os.getenv("KUBE_REQUEST_TIMEOUT", 15))
    )
    allowed_contexts: list[str] = Field(default_factory=list)


class SyncSettings(BaseModel):
    enabled: bool = Field(default=os.getenv("SYNC_ENABLED", "false").lower() == "true")
    schedule: str = Field(default=os.getenv("SYNC_SCHEDULE", "0 */12 * * *"))
    batch_size: int = Field(default=int(os.getenv("SYNC_BATCH_SIZE", 200)))


class SecuritySettings(BaseModel):
    allow_external_neo4j: bool = Field(
        default=os.getenv("ALLOW_EXTERNAL_NEOS", "false").lower() == "true"
    )
    allow_destructive_cypher: bool = Field(
        default=os.getenv("ALLOW_DESTRUCTIVE_CYPHER", "false").lower() == "true"
    )


class ExportSettings(BaseModel):
    default_format: str = Field(default=os.getenv("EXPORT_DEFAULT_FORMAT", "png"))
    allow_svg: bool = Field(default=os.getenv("EXPORT_ALLOW_SVG", "true").lower() == "true")


class Settings(BaseModel):
    platform: PlatformSettings = Field(default_factory=PlatformSettings)
    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    kubernetes: KubernetesSettings = Field(default_factory=KubernetesSettings)
    sync: SyncSettings = Field(default_factory=SyncSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    export: ExportSettings = Field(default_factory=ExportSettings)

    @classmethod
    def from_file(cls, path: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None) -> "Settings":
        config_path = Path(path or os.getenv("APP_CONFIG_FILE", "config/application.yaml"))
        data: Dict[str, Any] = {}
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as fp:
                data = yaml.safe_load(fp) or {}
        if overrides:
            data.update(overrides)
        return cls(**data)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_file()


def refresh_settings(new_data: Optional[Dict[str, Any]] = None) -> Settings:
    get_settings.cache_clear()  # type: ignore[attr-defined]
    merged = Settings.from_file(overrides=new_data)
    return merged
