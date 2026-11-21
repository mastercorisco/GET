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


def test_brief_contribution_template_endpoint(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    res = client.get("/api/packages/brief-contribution-template")
    assert res.status_code == 200
    assert "Resultado esperado desta sessão" in res.json()["template"]


def test_block_export_includes_llm_brief_and_response_brief(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id, "llm_notes": "só pontos ready"},
    )
    assert export.status_code == 200
    data = export.json()
    assert data["export_id"] in data["brief"]
    assert "só pontos ready" in data["brief"]
    pkg = json.loads(data["body"])
    brief = pkg.get("llm_brief") or {}
    assert brief.get("user_notes") == "só pontos ready"
    assert brief.get("export_id") == data["export_id"]


def test_block_export_brief_hints_when_notes_empty(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    assert export.status_code == 200
    assert "Contexto do utilizador" in export.json()["brief"]
    assert "Resultado esperado desta sessão" in export.json()["brief"]


def test_block_export_llm_shapes_anti_patterns(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    aps = pkg["llm_shapes"].get("anti_patterns") or []
    assert aps
    assert any("must_include" in line for line in aps)


def test_package_import_without_llm_brief_still_valid(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    pkg.pop("llm_brief", None)
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["core_idea"] = "Sem llm_brief"
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("nobrief.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert uploaded.status_code == 200


def test_block_export_includes_llm_shapes_and_full_lists(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    assert export.status_code == 200
    pkg = json.loads(export.json()["body"])
    assert "llm_shapes" in pkg
    assert pkg["llm_shapes"]["scope_kind"] == "block"
    cols = pkg["llm_shapes"].get("collections") or {}
    assert "payload.development_points[].lists.must_include" in cols
    assert cols["payload.development_points[].lists.must_include"].get("item_template") == {"text": ""}
    lists = pkg["payload"]["development_points"][0]["lists"]
    for key in (
        "development_guidance",
        "must_include",
        "questions_to_answer",
        "knowledge_item_ids",
    ):
        assert key in lists


def test_block_import_rejects_string_in_must_include(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["lists"]["must_include"] = ["texto solto"]
    bad = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("bad.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert bad.status_code == 400
    assert "incompatível" in bad.json()["detail"].lower()


def test_block_import_rejects_incomplete_point_lists(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["lists"].pop("development_guidance", None)
    bad = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("nolists.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert bad.status_code == 400
    detail = bad.json()["detail"].lower()
    assert "incompatível" in detail or "development_guidance" in detail


def test_package_import_without_llm_shapes_still_valid(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    pkg.pop("llm_shapes", None)
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["core_idea"] = "Sem llm_shapes"
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("nost.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert uploaded.status_code == 200


def test_block_roundtrip_preserves_point_uuid(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    exported_id = None
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            exported_id = row["id"]
            row["core_idea"] = "Alterado"
    assert exported_id == point_id
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("uuid.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert uploaded.status_code == 200
    for row in pkg["payload"]["development_points"]:
        assert row["id"] == exported_id


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


def test_block_export_includes_structure_anchor(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    assert pkg["schema_version"] == "1.0.1"
    anchor = pkg["payload"].get("structure_anchor") or {}
    assert anchor.get("fascicle_display_code") == "F01"
    assert anchor.get("position_among_blocks") == 1


def test_import_returns_conceptual_warnings_field(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("ok.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert uploaded.status_code == 200
    body = uploaded.json()
    assert "conceptual_warnings" in body
    assert isinstance(body["conceptual_warnings"], list)


def test_block_export_writes_merge_base(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    assert export.status_code == 200
    data = export.json()
    merge_base = Path(data["file_path"]).parent / "merge_base.json"
    assert merge_base.is_file()


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


def test_block_merge_point_update_when_status_differs(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["core_idea"] = "Com status errado na LLM"
            row["status"] = "approved"
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("st.json", json.dumps(pkg).encode(), "application/json")},
    )
    import_id = uploaded.json()["import_id"]
    merged = client.post(f"/api/projects/{pid}/packages/imports/{import_id}/merge").json()
    prop = next(
        p for p in merged["proposals"] if p["proposal_kind"] == "point_update" and p["target_item_id"] == point_id
    )
    assert prop["protected_touch"] is False
    merge_id = merged["id"]
    client.patch(
        f"/api/projects/{pid}/packages/merge/{merge_id}/proposals/{prop['id']}",
        json={"decision": "accepted", "destination": "project", "confirmed_protected": False},
    )
    assert client.post(f"/api/projects/{pid}/packages/merge/{merge_id}/consolidate").status_code == 200
    found = client.get(f"/api/development-points/{point_id}").json()
    assert found["core_idea"] == "Com status errado na LLM"
    assert found["status"] == "draft"


def test_block_merge_skips_unchanged_points_vs_current(client: TestClient, tmp_path: Path) -> None:
    """Proposta com proposed == estado actual do ponto não gera decisão."""
    pid, block_id, point_id = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    client.patch(f"/api/development-points/{point_id}", json={"core_idea": "Já na BD"})
    for row in pkg["payload"]["development_points"]:
        if row["id"] == point_id:
            row["core_idea"] = "Já na BD"
    uploaded = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("cur.json", json.dumps(pkg).encode(), "application/json")},
    )
    merged = client.post(
        f"/api/projects/{pid}/packages/imports/{uploaded.json()['import_id']}/merge"
    ).json()
    assert not [
        p
        for p in merged["proposals"]
        if p["proposal_kind"] == "point_update" and p["target_item_id"] == point_id
    ]


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
    base_lists = pkg["payload"]["development_points"][0]["lists"]
    pkg["payload"]["development_points"].append(
        {
            "id": "new_001",
            "sort_order": 2,
            "title": "Novo ponto LLM",
            "core_idea": "c",
            "intended_outcome": "o",
            "lists": dict(base_lists),
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

def test_block_import_rejects_unknown_block_id(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    pkg["scope"]["block_id"] = str(uuid.uuid4())
    pkg["payload"]["block"]["id"] = pkg["scope"]["block_id"]
    bad = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("orphan.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert bad.status_code == 400
    assert "não existe" in bad.json()["detail"].lower() or "incompatível" in bad.json()["detail"].lower()


def test_block_import_rejects_stale_display_code(client: TestClient, tmp_path: Path) -> None:
    pid, block_id, _ = _setup_block(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/packages/export",
        json={"scope_kind": "block", "node_id": block_id},
    )
    pkg = json.loads(export.json()["body"])
    pkg["payload"]["block"]["display_code"] = "F99_B99"
    bad = client.post(
        f"/api/projects/{pid}/packages/import",
        files={"file": ("stale_code.json", json.dumps(pkg).encode(), "application/json")},
    )
    assert bad.status_code == 400
    assert "display_code" in bad.json()["detail"].lower()

