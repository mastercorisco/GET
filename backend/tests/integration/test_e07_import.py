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


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _setup_fascicle_export(client: TestClient, tmp_path: Path) -> tuple[str, str, str]:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    fascicle = _create_node(client, pid, "fascicle", "Fascículo raiz", None)["node"]
    item_id = _project_knowledge(client, pid)
    assoc = client.post(
        f"/api/document-nodes/{fascicle['id']}/associations",
        json={"knowledge_item_id": item_id, "role": "mandatory_content"},
    )
    assert assoc.status_code == 200
    assert client.post(f"/api/projects/{pid}/baselines/publish").status_code == 200
    export = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle['id']}",
        json={"profile": "discussion"},
    )
    assert export.status_code == 200
    return pid, fascicle["id"], item_id


def test_import_happy_path_update_and_consolidate(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, item_id = _setup_fascicle_export(client, tmp_path)
    export = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle_id}",
        json={"profile": "discussion"},
    ).json()
    payload = json.loads(Path(export["file_path"]).read_text(encoding="utf-8"))
    for row in payload.get("protected_context", {}).get("knowledge_items", []):
        if row.get("id") == item_id:
            row["title"] = "Título revisto via import"
            row["content"] = "Conteúdo revisto via import"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    uploaded = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("returned.json", body, "application/json")},
    )
    assert uploaded.status_code == 200
    import_id = uploaded.json()["id"]

    merged = client.post(
        f"/api/projects/{pid}/imports/{import_id}/merge",
        json={"fascicle_node_id": fascicle_id},
    )
    assert merged.status_code == 200
    proposals = merged.json()["proposals"]
    update = next((p for p in proposals if p["proposal_kind"] == "update" and p["target_item_id"] == item_id), None)
    assert update is not None

    merge_id = merged.json()["id"]
    decided = client.patch(
        f"/api/projects/{pid}/imports/merge/{merge_id}/proposals/{update['id']}",
        json={"decision": "accepted", "destination": "project", "confirmed_protected": False},
    )
    assert decided.status_code == 200

    before = client.get(f"/api/knowledge/{item_id}").json()
    rev_before = before.get("latest_revision_num") or 0

    consolidated = client.post(f"/api/projects/{pid}/imports/merge/{merge_id}/consolidate")
    assert consolidated.status_code == 200
    assert consolidated.json()["backup_id"]

    after = client.get(f"/api/knowledge/{item_id}").json()
    assert after["latest_revision_num"] == rev_before + 1
    assert after["title"] == "Título revisto via import"


def test_upload_truncated_json_rejected(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    pid = _project(client)["id"]
    bad = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("bad.json", b'{"package_type":', "application/json")},
    )
    assert bad.status_code == 400


def test_upload_future_schema_rejected(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    pid = _project(client)["id"]
    body = json.dumps(
        {"package_type": "fascicle_roundtrip", "schema_version": "99.0.0", "schema_name": "get_fascicle_roundtrip"}
    ).encode("utf-8")
    bad = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("future.json", body, "application/json")},
    )
    assert bad.status_code == 400


def test_omission_does_not_remove_item(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, item_id = _setup_fascicle_export(client, tmp_path)
    export_path = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle_id}",
        json={"profile": "discussion"},
    ).json()["file_path"]
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    payload["protected_context"]["knowledge_items"] = []
    payload["editable_knowledge"] = {"knowledge_items": [], "decisions": [], "open_questions": []}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    uploaded = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("omit.json", body, "application/json")},
    )
    assert uploaded.status_code == 200
    merged = client.post(
        f"/api/projects/{pid}/imports/{uploaded.json()['id']}/merge",
        json={"fascicle_node_id": fascicle_id},
    )
    assert merged.status_code == 200
    assert item_id in merged.json()["summary"]["no_op_omissions"]
    removal = next((p for p in merged.json()["proposals"] if p["proposal_kind"] == "removal"), None)
    assert removal is None
    rev = client.get(f"/api/knowledge/{item_id}").json().get("latest_revision_num") or 0
    assert rev == 1


def test_protected_touch_requires_confirmation(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, item_id = _setup_fascicle_export(client, tmp_path)
    export_path = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle_id}",
        json={"profile": "discussion"},
    ).json()["file_path"]
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    for row in payload["protected_context"]["knowledge_items"]:
        if row["id"] == item_id:
            row["states"]["approval"] = "rejected"
            row["title"] = "Título alterado"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    import_id = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("prot.json", body, "application/json")},
    ).json()["id"]
    merged = client.post(
        f"/api/projects/{pid}/imports/{import_id}/merge",
        json={"fascicle_node_id": fascicle_id},
    ).json()
    prop = next(p for p in merged["proposals"] if p["target_item_id"] == item_id)
    assert prop["protected_touch"] is True
    client.patch(
        f"/api/projects/{pid}/imports/merge/{merged['id']}/proposals/{prop['id']}",
        json={"decision": "accepted", "destination": "project", "confirmed_protected": False},
    )
    blocked = client.post(f"/api/projects/{pid}/imports/merge/{merged['id']}/consolidate")
    assert blocked.status_code == 400


def test_explicit_removal_proposal(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, item_id = _setup_fascicle_export(client, tmp_path)
    export_path = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle_id}",
        json={"profile": "discussion"},
    ).json()["file_path"]
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    payload["proposed_removals"] = [{"target_id": item_id, "reason": "teste"}]
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    import_id = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("rem.json", body, "application/json")},
    ).json()["id"]
    merged = client.post(
        f"/api/projects/{pid}/imports/{import_id}/merge",
        json={"fascicle_node_id": fascicle_id},
    ).json()
    removal = next(p for p in merged["proposals"] if p["proposal_kind"] == "removal")
    assert removal["target_item_id"] == item_id


def test_unknown_uuid_quarantine_on_merge(client: TestClient, tmp_path: Path) -> None:
    pid, fascicle_id, _item_id = _setup_fascicle_export(client, tmp_path)
    export_path = client.post(
        f"/api/projects/{pid}/exports/fascicle/{fascicle_id}",
        json={"profile": "discussion"},
    ).json()["file_path"]
    payload = json.loads(Path(export_path).read_text(encoding="utf-8"))
    alien = str(uuid.uuid4())
    clone = json.loads(json.dumps(payload["protected_context"]["knowledge_items"][0]))
    clone["id"] = alien
    clone["title"] = "Intruder"
    payload["editable_knowledge"]["knowledge_items"].append(clone)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    import_id = client.post(
        f"/api/projects/{pid}/imports",
        files={"file": ("alien.json", body, "application/json")},
    ).json()["id"]
    merged = client.post(
        f"/api/projects/{pid}/imports/{import_id}/merge",
        json={"fascicle_node_id": fascicle_id},
    ).json()
    assert alien in merged["summary"]["quarantined_ids"]