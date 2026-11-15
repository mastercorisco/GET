from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app
from app.services.project_service import ensure_template_version
from app.services.workspace_service import workspace_session


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _workspace(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/api/workspace/create",
        json={"root_path": str(tmp_path / "workspace"), "local_user_name": "tester"},
    )
    assert response.status_code == 200


def _ensure_library(client: TestClient) -> None:
    client.post(
        "/api/knowledge",
        json={
            "title": "Semente biblioteca",
            "content": "conteúdo",
            "origin_context": "teste",
        },
    )


def _template_v1(client: TestClient) -> str:
    templates = client.get("/api/projects/templates")
    assert templates.status_code == 200
    return templates.json()[0]["versions"][0]["id"]


def test_create_project_without_prior_knowledge_unit(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    v1_id = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "Projeto sem unidade prévia",
            "intervention_type": "brownfield",
        },
    )
    assert created.status_code == 200
    assert created.json()["library_version"] == 1


def test_project_pins_library_and_keeps_template_version(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1_id = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v1_id,
            "name": "Projeto A",
            "intervention_type": "brownfield",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["template_version_id"] == v1_id
    assert body["template_version"] == 1
    assert body["library_version"] == 1

    with workspace_session(get_settings()) as (session, _paths):
        ensure_template_version(session, 2)

    later = client.get(f"/api/projects/{body['id']}")
    assert later.status_code == 200
    assert later.json()["template_version_id"] == v1_id
    assert later.json()["template_version"] == 1


def test_instance_parent_must_belong_to_same_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _template_v1(client)
    p1 = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P1", "intervention_type": "brownfield"},
    ).json()
    p2 = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P2", "intervention_type": "brownfield"},
    ).json()
    root = client.post(
        f"/api/projects/{p1['id']}/instances",
        json={"kind": "system", "name": "Sistema 1"},
    ).json()
    other_root = client.post(
        f"/api/projects/{p2['id']}/instances",
        json={"kind": "system", "name": "Sistema 2"},
    ).json()
    denied = client.post(
        f"/api/projects/{p1['id']}/instances",
        json={"kind": "equipment", "name": "Filho inválido", "parent_id": other_root["id"]},
    )
    assert denied.status_code == 400
    allowed = client.post(
        f"/api/projects/{p1['id']}/instances",
        json={"kind": "equipment", "name": "Filho válido", "parent_id": root["id"]},
    )
    assert allowed.status_code == 200
    assert allowed.json()["parent_id"] == root["id"]
    assert allowed.json()["depth"] == 1


def test_project_knowledge_isolated_from_library(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P-K", "intervention_type": "brownfield"},
    ).json()
    client.post(
        "/api/knowledge",
        json={
            "title": "Biblioteca isolada",
            "content": "só biblioteca",
            "origin_context": "teste",
        },
    )
    client.post(
        "/api/knowledge",
        json={
            "title": "Unidade de projeto",
            "content": "só projeto",
            "origin_context": "teste",
            "scope_type": "project",
            "scope_id": project["id"],
        },
    )
    library = client.get("/api/knowledge", params={"scope_type": "library"})
    project_items = client.get(
        "/api/knowledge",
        params={"scope_type": "project", "scope_id": project["id"]},
    )
    assert library.status_code == 200
    assert project_items.status_code == 200
    library_titles = {item["title"] for item in library.json()}
    project_titles = {item["title"] for item in project_items.json()}
    assert "Unidade de projeto" in project_titles
    assert "Unidade de projeto" not in library_titles
    assert project_items.json()[0]["scope_type"] == "project"