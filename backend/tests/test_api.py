import pytest
from fastapi.testclient import TestClient

from app.core.security import verify_token
from app.main import app
from app.services.import_service import ImportService


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[verify_token] = lambda: "test"
    yield
    app.dependency_overrides.pop(verify_token, None)


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_preset_queries():
    client = TestClient(app)
    response = client.get("/api/preset-queries")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_import_mock(monkeypatch):
    class DummyImport(ImportService):
        def import_cluster(self, use_mock: bool = False):  # type: ignore[override]
            return (1, 1)

    app.state.import_service = DummyImport()
    client = TestClient(app)
    response = client.post("/api/import/k8s?mock=true")
    assert response.status_code == 200
    assert response.json()["nodes"] == 1
