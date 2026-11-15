from __future__ import annotations

import json
import zipfile
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]


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


def _project(client: TestClient, name: str = "Export project") -> dict:
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


def _validate_json(instance: dict, schema_name: str) -> None:
    schema_path = REPO_ROOT / "schemas" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    resolver = jsonschema.RefResolver(
        base_uri=schema_path.as_uri(),
        referrer=schema,
        store={
            "https://eda.local/get/schemas/common.schema.json": json.loads(
                (REPO_ROOT / "schemas/common.schema.json").read_text(encoding="utf-8")
            ),
            "https://eda.local/get/schemas/knowledge-item.schema.json": json.loads(
                (REPO_ROOT / "schemas/knowledge-item.schema.json").read_text(encoding="utf-8")
            ),
        },
    )
    jsonschema.validate(instance=instance, schema=schema, resolver=resolver)


def _project_knowledge(client: TestClient, project_id: str) -> str:
    created = client.post(
        "/api/knowledge",
        json={
            "title": "Unidade exportável",
            "content": "corpo",
            "origin_context": "teste",
            "scope_type": "project",
            "scope_id": project_id,
        },
    )
    assert created.status_code == 200
    item_id = created.json()["id"]
    assert client.post(f"/api/knowledge/{item_id}/conclude").status_code == 200
    return item_id


def test_export_master_and_fascicle_roundtrip(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    fascicle = _create_node(client, pid, "fascicle", "Fascículo raiz", None)["node"]
    item_id = _project_knowledge(client, pid)
    assoc = client.post(
        f"/api/document-nodes/{fascicle['id']}/associations",
        json={
            "knowledge_item_id": item_id,
            "role": "mandatory_content",
        },
    )
    assert assoc.status_code == 200

    no_baseline = client.post(f"/api/projects/{pid}/exports/master", json={"profile": "discussion"})
    assert no_baseline.status_code == 400

    published = client.post(f"/api/projects/{pid}/baselines/publish")
    assert published.status_code == 200
    assert published.json()["revision"] == 1

    latest = client.get(f"/api/projects/{pid}/baselines/latest")
    assert latest.status_code == 200
    assert latest.json()["id"] == published.json()["id"]

    master = client.post(
        f"/api/projects/{pid}/exports/master",
        json={"profile": "discussion", "write_zip": True},
    )
    assert master.status_code == 200
    body = master.json()
    master_path = Path(body["file_path"])
    assert master_path.is_file()
    assert body["sha256"]
    master_data = json.loads(master_path.read_text(encoding="utf-8"))
    assert master_data["validation"]["status"] == "valid"
    _validate_json(master_data, "master.schema.json")

    master2 = client.post(f"/api/projects/{pid}/exports/master", json={"profile": "discussion"})
    assert master2.status_code == 200
    assert master2.json()["sha256"] == body["sha256"]

    fascicle_export = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle['id']}",
        json={"profile": "discussion"},
    )
    assert fascicle_export.status_code == 200
    fascicle_path = Path(fascicle_export.json()["file_path"])
    assert fascicle_path.is_file()
    fascicle_data = json.loads(fascicle_path.read_text(encoding="utf-8"))
    assert fascicle_data["validation"]["status"] == "valid"
    _validate_json(fascicle_data, "fascicle-roundtrip.schema.json")

    md_path = fascicle_path.with_suffix(".md")
    assert md_path.is_file()
    assert "Não reimportável" in md_path.read_text(encoding="utf-8")

    zip_path = body.get("zip_path")
    assert zip_path
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())
        assert "master_discussion.json" in names
        assert "validation.json" in names
        assert any(name.endswith(".json") and name.startswith("F") for name in names)

    listing = client.get(f"/api/projects/{pid}/exports")
    assert listing.status_code == 200
    assert len(listing.json()) >= 2