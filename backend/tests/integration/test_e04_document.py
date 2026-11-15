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


def _project(client: TestClient, name: str = "Doc project") -> dict:
    _ensure_library(client)
    v1 = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": name, "intervention_type": "brownfield"},
    )
    assert created.status_code == 200
    return created.json()


def _create_node(client: TestClient, project_id: str, node_type: str, title: str, parent_id: str | None):
    response = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": node_type, "title": title, "parent_id": parent_id},
    )
    assert response.status_code == 200
    return response.json()


def test_document_tree_display_codes(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    f = _create_node(client, pid, "fascicle", "Fascículo 1", None)["node"]
    b = _create_node(client, pid, "block", "Bloco 1", f["id"])["node"]
    s = _create_node(client, pid, "section", "Secção 1", b["id"])["node"]
    ss = _create_node(client, pid, "subsection", "Subsecção 1", s["id"])["node"]

    assert f["display_code"] == "F01"
    assert b["display_code"] == "F01_B01"
    assert s["display_code"] == "F01_B01_S01"
    assert ss["display_code"] == "F01_B01_S01_SS01"

    listing = client.get(f"/api/projects/{pid}/document-nodes")
    assert listing.status_code == 200
    codes = [n["display_code"] for n in listing.json()["nodes"]]
    assert codes == ["F01", "F01_B01", "F01_B01_S01", "F01_B01_S01_SS01"]


def test_fifth_depth_warning_without_blocking(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    f = _create_node(client, pid, "fascicle", "F", None)["node"]
    b = _create_node(client, pid, "block", "B", f["id"])["node"]
    s = _create_node(client, pid, "section", "S", b["id"])["node"]
    ss = _create_node(client, pid, "subsection", "SS", s["id"])["node"]
    extra = client.post(
        f"/api/projects/{pid}/document-nodes",
        json={"node_type": "block", "title": "Quinto nível", "parent_id": ss["id"]},
    )
    assert extra.status_code == 200
    node = extra.json()["node"]
    assert node["depth"] == 5
    assert node["depth_warning"] is True


def test_move_sibling_renumbers(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    f = _create_node(client, pid, "fascicle", "F", None)["node"]
    b1 = _create_node(client, pid, "block", "B1", f["id"])["node"]
    b2 = _create_node(client, pid, "block", "B2", f["id"])["node"]
    assert b1["display_code"] == "F01_B01"
    assert b2["display_code"] == "F01_B02"

    moved = client.post(
        f"/api/projects/{pid}/document-nodes/{b2['id']}/move",
        json={"direction": "up"},
    )
    assert moved.status_code == 200
    body = moved.json()
    assert body["node"]["display_code"] == "F01_B01"
    changes = {c["node_id"]: c for c in body["renumber_changes"]}
    assert b2["id"] in changes
    assert changes[b2["id"]]["old_code"] == "F01_B02"
    assert changes[b2["id"]]["new_code"] == "F01_B01"


def test_association_and_invalid_role(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    item = client.post(
        "/api/knowledge",
        json={
            "title": "Ref doc",
            "content": "texto",
            "origin_context": "teste",
            "scope_type": "project",
            "scope_id": pid,
        },
    ).json()
    node = _create_node(client, pid, "fascicle", "F", None)["node"]

    ok = client.post(
        f"/api/document-nodes/{node['id']}/associations",
        json={
            "knowledge_item_id": item["id"],
            "role": "mandatory_content",
            "usage_instruction": "Incluir na redação",
        },
    )
    assert ok.status_code == 200
    assert ok.json()["knowledge_item_id"] == item["id"]
    assert ok.json()["role"] == "mandatory_content"

    bad = client.post(
        f"/api/document-nodes/{node['id']}/associations",
        json={"knowledge_item_id": item["id"], "role": "not_a_role"},
    )
    assert bad.status_code == 400


def test_move_to_descendant_rejected(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    f = _create_node(client, pid, "fascicle", "F", None)["node"]
    b = _create_node(client, pid, "block", "B", f["id"])["node"]
    denied = client.post(
        f"/api/projects/{pid}/document-nodes/{f['id']}/move",
        json={"new_parent_id": b["id"]},
    )
    assert denied.status_code == 400