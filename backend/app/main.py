from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, config, cypher, export, graph, importer, metadata
from app.core.logging import configure_logging
from app.core.settings import get_settings
from app.services.import_service import ImportService

configure_logging()
settings = get_settings()
app = FastAPI(title="云原生攻击路径平台", version="1.0.0")
app.state.import_service = ImportService()

origins = settings.platform.allow_cors_origins or [settings.platform.frontend_url]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(config.router)
app.include_router(importer.router)
app.include_router(cypher.router)
app.include_router(graph.router)
app.include_router(metadata.router)
app.include_router(export.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup() -> None:
    app.state.import_service.start_scheduler()


@app.on_event("shutdown")
def on_shutdown() -> None:
    app.state.import_service.shutdown()
