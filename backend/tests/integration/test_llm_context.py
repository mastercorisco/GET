from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _workspace(client: TestClient, tmp_path: Path) -> None:
    assert client.post(
        "/api/workspace/create",
        json={"root_path": str(tmp_path / "workspace"), "local_user_name": "tester"},
    ).status_code == 200


def test_project_llm_context_roundtrip(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post(
        "/api/knowledge",
        json={"title": "Seed", "content": "c", "origin_context": "t"},
    )
    v1 = client.get("/api/projects/templates").json()[0]["versions"][0]["id"]
    pid = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "Ctx", "intervention_type": "brownfield"},
    ).json()["id"]

    patched = client.patch(
        f"/api/projects/{pid}/llm-context",
        json={
            "context": {
                "code": "BJ_DCS",
                "owner": "EDA",
                "document_type": "Caderno de Encargos",
                "location": {"site": "Belo Jardim"},
            }
        },
    )
    assert patched.status_code == 200
    assert patched.json()["context"]["code"] == "BJ_DCS"

    loaded = client.get(f"/api/projects/{pid}/llm-context")
    assert loaded.status_code == 200
    assert loaded.json()["context"]["owner"] == "EDA"