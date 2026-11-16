from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app

from tests.integration.test_e06_export import (
    _create_node,
    _project,
    _project_knowledge,
    _workspace,
)
from tests.integration.test_e07_import import _setup_fascicle_export


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _setup_block(client: TestClient, tmp_path: Path) -> tuple[str, str, str]:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    fascicle = _create_node(client, pid, "fascicle", "Fascículo", None)["node"]
    block = _create_node(client, pid, "block", "Bloco teste", fascicle["id"])["node"]
    point = client.post(
        f"/api/blocks/{block['id']}/development-points",
        json={"title": "Ponto A", "core_idea": "ideia", "intended_outcome": "resultado"},
    )
    assert point.status_code == 200
    assert client.post(f"/api/projects/{pid}/baselines/publish").status_code == 200
    return pid, block["id"], point.json()["id"]


def test_package_export_import_rejects_bad_rules_hash(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, _ = _setup_fascicle_export(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "fascicle", "node_id": fascicle_id},
    )
    assert export.status_code == 200
    pkg = json.loads(export.json()["body"])
    pkg["rules_hash"] = "0" * 64
    bad = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("bad.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert bad.status_code == 400
    assert "incompatível" in bad.json()["detail"].lower()


def test_fascicle_package_roundtrip(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, item_id = _setup_fascicle_export(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "fascicle", "node_id": fascicle_id},
    )
    assert export.status_code == 200
    export_id = export.json()["export_id"]
    pkg = json.loads(export.json()["body"])
    inner = pkg["payload"]
    for row in inner.get("protected_context", {}).get("knowledge_items", []):
        if row.get("id") == item_id:
            row["title"] = "Título via GET-PACKAGE"
            row["content"] = "Conteúdo via GET-PACKAGE"
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("ret.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert uploaded.status_code == 200
    import_id = uploaded.json()["import_id"]
    merged = client.post(f"/api/projects/{pid}/packages/imports/{import_id}/merge")
    assert merged.status_code == 200
    proposals = merged.json()["proposals"]
    update = next((p for p in proposals if p["proposal_kind"] == "update" and p["target_item_id"] == item_id), None)
    assert update is not None
    merge_id = merged.json()["id"]
    dec = client.patch(
        f"/api/projects/{pid}/packages/merge/{merge_id}/proposals/{update['id']}",
        json={"decision": "accepted", "destination": "project", "confirmed_protected": False},
    )
    assert dec.status_code == 200
    consolidated = client.post(f"/api/projects/{pid}/packages/merge/{merge_id}/consolidate")
    assert consolidated.status_code == 200
    after = client.get(f"/api/knowledge/{item_id}").json()
    assert after["title"] == "Título via GET-PACKAGE"
    assert export_id.startswith("PKG-FASC")


def test_block_package_roundtrip(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    assert export.status_code == 200
    pkg = json.loads(export.json()["body"])
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["core_idea"] = "Ideia melhorada"
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("blk.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert uploaded.status_code == 200
    import_id = uploaded.json()["import_id"]
    merged = client.post(f"/api/projects/{pid}/packages/imports/{import_id}/merge")
    assert merged.status_code == 200
    prop = next(
        p for p in merged.json()["proposals"] if p["proposal_kind"] == "point_update" and p["target_item_id"] == point_id
    )
    merge_id = merged.json()["id"]
    client.patch(
        f"/api/projects/{pid}/packages/merge/{merge_id}/proposals/{prop['id']}",
        json={"decision": "accepted", "destination": "project", "confirmed_protected": False},
    )
    assert client.post(f"/api/projects/{pid}/packages/merge/{merge_id}/consolidate").status_code == 200
    found = client.get(f"/api/development-points/{point_id}").json()
    assert found["core_idea"] == "Ideia melhorada"


def test_block_omission_keeps_point(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    pkg["payload"]["development_points"] = []
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("omit.json", json.dumps(pkg).encode(), "application/json")},
    )
    import_id = uploaded.json()["import_id"]
    merged = client.post(f"/api/projects/{pid}/packages/imports/{import_id}/merge").json()
    assert point_id in merged["summary"]["no_op_omissions"]
    points = client.get(f"/api/blocks/{block_id}").json()["points"]
    assert any(p["id"] == point_id for p in points)


def test_new_point_via_package(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    pkg["payload"]["development_points"].append(
        {
            "id": "new_001",
            "sort_order": 2,
            "title": "Novo ponto LLM",
            "core_idea": "c",
            "intended_outcome": "o",
            "lists": {},
            "status": "draft",
            "llm_freedom": "bounded",
            "template_id": None,
            "needs_review": False,
        }
    )
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("newp.json", json.dumps(pkg).encode(), "application/json")},
    )
    import_id = uploaded.json()["import_id"]
    merged = client.post(f"/api/projects/{pid}/packages/imports/{import_id}/merge").json()
    create = next(p for p in merged["proposals"] if p["proposal_kind"] == "point_create")
    merge_id = merged["id"]
    assert (
        client.patch(
            f"/api/projects/{pid}/packages/merge/{merge_id}/proposals/{create['id']}",
            json={"decision": "accepted", "destination": "project", "confirmed_protected": False},
        ).status_code
        == 200
    )
    assert client.post(f"/api/projects/{pid}/packages/merge/{merge_id}/consolidate").status_code == 200
    points = client.get(f"/api/blocks/{block_id}").json()["points"]
    assert any(p["title"] == "Novo ponto LLM" for p in points)