from __future__ import annotations

from pathlib import Path

import json
import jsonschema
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.deps import get_settings
from app.main import app
from app.models.document import DocumentNode
from app.services.structure_seed.bootstrap_contract import build_bootstrap_contract
from app.services.workspace_service import workspace_session


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def _workspace(client: TestClient, tmp_path: Path) -> None:
    assert (
        client.post(
            "/api/workspace/create",
            json={"root_path": str(tmp_path / "ws"), "local_user_name": "tester"},
        ).status_code
        == 200
    )


def _ensure_library(client: TestClient) -> None:
    client.post(
        "/api/knowledge",
        json={"title": "Lib", "content": "x", "origin_context": "test"},
    )


def _generic_template_v1(client: TestClient) -> str:
    templates = client.get("/api/projects/templates")
    assert templates.status_code == 200
    for tpl in templates.json():
        if tpl["code"] == "generic-structure-v1":
            v1 = next(v for v in tpl["versions"] if v["version"] == 1)
            return v1["id"]
    raise AssertionError("Modelo generic-structure-v1 em falta")


def test_structure_catalog_list_and_contract(client: TestClient) -> None:
    listed = client.get("/api/structure-catalogs")
    assert listed.status_code == 200
    ids = {c["id"] for c in listed.json()["catalogs"]}
    assert "generic_example_v1" in ids
    assert "ctbj_v3" in ids

    contract = client.get("/api/structure-catalogs/generic_example_v1/bootstrap-contract")
    assert contract.status_code == 200
    body = contract.json()
    assert body["schema"] == "GET-STRUCTURE-CONTRACT"
    assert body["catalog"]["id"] == "generic_example_v1"
    assert len(body["fascicles"]) == 1


def test_bootstrap_contract_matches_schema() -> None:
    repo = Path(__file__).resolve().parents[3]
    schema = json.loads((repo / "schemas" / "get_structure_contract.schema.json").read_text(encoding="utf-8"))
    body = build_bootstrap_contract("generic_example_v1")
    jsonschema.validate(instance=body, schema=schema)


def test_workbook_structure_download(client: TestClient) -> None:
    res = client.get("/api/structure-catalogs/generic_example_v1/workbook-structure.xlsx")
    assert res.status_code == 200
    assert "spreadsheet" in res.headers.get("content-type", "")


def test_create_project_generic_seeds_tree(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _generic_template_v1(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v1,
            "name": "Genérico",
            "intervention_type": "generic",
        },
    )
    assert created.status_code == 200
    pid = created.json()["id"]
    settings = get_settings()
    with workspace_session(settings) as (session, _paths):
        fascicles = session.scalar(
            select(func.count())
            .select_from(DocumentNode)
            .where(DocumentNode.project_id == pid, DocumentNode.node_type == "fascicle")
        )
        blocks = session.scalar(
            select(func.count())
            .select_from(DocumentNode)
            .where(DocumentNode.project_id == pid, DocumentNode.node_type == "block")
        )
    assert fascicles == 1
    assert blocks == 2