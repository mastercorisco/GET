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
    root = tmp_path / "workspace"
    response = client.post(
        "/api/workspace/create",
        json={"root_path": str(root), "local_user_name": "tester"},
    )
    assert response.status_code == 200


def test_delete_draft_knowledge_and_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post(
        "/api/knowledge",
        json={
            "title": "Rascunho apagar",
            "content": "texto",
            "origin_context": "teste",
        },
    )
    listed = client.get("/api/knowledge", params={"scope_type": "library"})
    item_id = listed.json()[0]["id"]
    deleted = client.delete(f"/api/knowledge/{item_id}")
    assert deleted.status_code == 200
    assert deleted.json()["mode"] == "deleted"
    assert client.get("/api/knowledge", params={"scope_type": "library"}).json() == []

    templates = client.get("/api/projects/templates").json()
    v1 = templates[0]["versions"][0]["id"]
    project = client.post(
        "/api/projects",
        json={
            "template_version_id": v1,
            "name": "Projeto temporário",
            "intervention_type": "brownfield",
        },
    ).json()
    pid = project["id"]
    assert client.delete(f"/api/projects/{pid}").status_code == 204
    assert client.get("/api/projects").json() == []