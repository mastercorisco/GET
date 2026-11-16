from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.domain.block.export import deterministic_exchange_json
from app.main import app
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
    return templates.json()[0]["versions"][0]["id"]


def _project(client: TestClient) -> dict:
    _ensure_library(client)
    v1 = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "Block DP project", "intervention_type": "brownfield"},
    )
    assert created.status_code == 200
    return created.json()


def _block_tree(client: TestClient, project_id: str) -> str:
    fascicle = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": "fascicle", "title": "Fascículo teste", "parent_id": None},
    ).json()["node"]
    block = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": "block", "title": "Perda de referências remotas", "parent_id": fascicle["id"]},
    ).json()["node"]
    return block["id"]


def test_block_points_crud_reorder_export(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    block_id = _block_tree(client, project["id"])

    client.patch(
        f"/api/blocks/{block_id}",
        json={
            "objective": "Definir comportamento local",
            "scope": "Autonomia perante SCADA",
            "target_output": {"format": "spec_section"},
        },
    )

    premise = client.post(
        "/api/premises",
        json={
            "owner_kind": "block",
            "owner_id": block_id,
            "statement": "O controlador local dispõe das variáveis necessárias.",
            "importance": "mandatory",
            "source_type": "operational_experience",
            "confidence": "confirmed",
        },
    )
    assert premise.status_code == 200

    p1 = client.post(
        f"/api/blocks/{block_id}/development-points",
        json={"title": "Autonomia SCADA", "template_id": "failure_behavior"},
    )
    assert p1.status_code == 200
    pid = p1.json()["id"]

    client.patch(
        f"/api/development-points/{pid}",
        json={
            "core_idea": "A indisponibilidade do SCADA não impede operação segura local.",
            "lists": {
                "development_guidance": ["Distinguir supervisão e controlo."],
                "perspectives": ["operational"],
                "questions_to_answer": [{"prompt": "condição desencadeadora", "answer": ""}],
                "must_include": [{"text": "Deteção de timeout"}],
                "limits_and_exclusions": [],
                "examples": [],
                "open_questions": [],
                "acceptance_criteria": ["Não introduz valores temporais não aprovados."],
                "knowledge_item_ids": [],
                "reference_ids": [],
            },
            "status": "ready",
        },
    )

    p2 = client.post(
        f"/api/blocks/{block_id}/development-points",
        json={"title": "Segundo ponto"},
    )
    assert p2.status_code == 200
    p2_id = p2.json()["id"]

    reordered = client.post(
        f"/api/blocks/{block_id}/development-points/reorder",
        json={"point_ids": [p2_id, pid]},
    )
    assert reordered.status_code == 200
    assert [p["id"] for p in reordered.json()["points"]] == [p2_id, pid]

    preview = client.get(f"/api/blocks/{block_id}/exchange-package")
    assert preview.status_code == 200
    package = preview.json()
    assert package["get_export"]["schema"] == "GET-LLM"
    assert len(package["preparation"]["development_points"]) == 1

    schema_path = Path(__file__).resolve().parents[3] / "schemas" / "get_llm_export.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=package, schema=schema)

    written = client.post(f"/api/blocks/{block_id}/exchange-package")
    assert written.status_code == 200
    body = written.json()
    assert Path(body["file_path"]).is_file()
    assert Path(body["markdown_path"]).is_file()
    assert "Autonomia SCADA" in Path(body["markdown_path"]).read_text(encoding="utf-8")


def test_failure_behavior_template_prompts_only(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    block_id = _block_tree(client, _project(client)["id"])
    created = client.post(
        f"/api/blocks/{block_id}/development-points",
        json={"template_id": "failure_behavior"},
    ).json()
    prompts = [q["prompt"] for q in created["lists"]["questions_to_answer"]]
    assert "condição desencadeadora" in prompts
    assert "intervenção do operador" in prompts
    assert created["title"] == ""


def test_deterministic_export(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    block_id = _block_tree(client, _project(client)["id"])
    pid = client.post(
        f"/api/blocks/{block_id}/development-points",
        json={"title": "P"},
    ).json()["id"]
    client.patch(
        f"/api/development-points/{pid}",
        json={
            "core_idea": "Afirmação técnica mínima.",
            "lists": {"development_guidance": ["Uma orientação"]},
            "status": "ready",
        },
    )
    settings = get_settings()
    with workspace_session(settings) as (session, _paths):
        a = deterministic_exchange_json(session, block_id)
        b = deterministic_exchange_json(session, block_id)
    assert a == b


def test_catalog_help_fallback(client: TestClient) -> None:
    res = client.get("/api/catalogs/help")
    assert res.status_code == 200
    assert "fields" in res.json()