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
    return client.get("/api/projects/templates").json()[0]["versions"][0]["id"]


def _project(client: TestClient) -> dict:
    _ensure_library(client)
    v1 = _template_v1(client)
    created = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "LLM gen", "intervention_type": "brownfield"},
    )
    assert created.status_code == 200
    return created.json()


def _block_with_ready_point(client: TestClient, project_id: str) -> tuple[str, str]:
    fascicle = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": "fascicle", "title": "Fascículo LLM", "parent_id": None},
    ).json()["node"]
    block = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": "block", "title": "Bloco LLM", "parent_id": fascicle["id"]},
    ).json()["node"]
    client.patch(
        f"/api/blocks/{block['id']}",
        json={
            "objective": "Objectivo",
            "scope": "Âmbito",
            "target_output": {"format": "spec_section"},
        },
    )
    point = client.post(
        f"/api/blocks/{block['id']}/development-points",
        json={"title": "Ponto", "template_id": "failure_behavior"},
    ).json()["id"]
    client.patch(
        f"/api/development-points/{point}",
        json={
            "core_idea": "Ideia central.",
            "lists": {
                "development_guidance": ["Orientação."],
                "perspectives": ["operational"],
                "questions_to_answer": [],
                "must_include": [],
                "limits_and_exclusions": [],
                "examples": [],
                "open_questions": [],
                "acceptance_criteria": ["Critério."],
                "knowledge_item_ids": [],
                "reference_ids": [],
            },
            "status": "ready",
        },
    )
    return fascicle["id"], block["id"]


def _validate_llm_export(instance: dict) -> None:
    schema_path = REPO_ROOT / "schemas" / "get_llm_export.schema.json"
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


def test_llm_generation_zip_without_baseline(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    _fascicle_id, block_id = _block_with_ready_point(client, pid)

    term_resp = client.post(
        "/api/terminology",
        json={
            "scope_type": "library",
            "preferred_term": "Adjudicatário",
            "definition": "Entidade que adjudica o contracto.",
        },
    )
    assert term_resp.status_code == 200

    response = client.post(
        f"/api/projects/{pid}/exports/llm-generation",
        json={"profile": "discussion", "include_draft": False},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["zip_path"]
    assert Path(body["zip_path"]).is_file()
    assert Path(body["file_path"]).is_file()
    assert body["manifest"]["schema"] == "GET-LLM-PACKAGE"
    kinds = {f["kind"] for f in body["manifest"]["files"]}
    assert kinds >= {"project_master", "fascicle", "block", "terminology_glossary"}

    with zipfile.ZipFile(body["zip_path"], "r") as zf:
        names = set(zf.namelist())
        assert "master_discussion_llm.json" in names or any(n.startswith("master_") and n.endswith("_llm.json") for n in names)
        assert "manifest.json" in names
        master_name = next(n for n in names if n.startswith("master_") and n.endswith("_llm.json"))
        fascicle_name = next(f["path"] for f in body["manifest"]["files"] if f["kind"] == "fascicle")
        block_name = next(f["path"] for f in body["manifest"]["files"] if f["kind"] == "block")
        assert fascicle_name in names and block_name in names
        master_data = json.loads(zf.read(master_name))
        fascicle_data = json.loads(zf.read(fascicle_name))
        block_data = json.loads(zf.read(block_name))
        assert master_data["get_export"]["export_type"] == "project_master"
        assert fascicle_data["get_export"]["export_type"] == "fascicle"
        assert block_data["get_export"]["export_type"] == "block"
        block_paths = [f["path"] for f in body["manifest"]["files"] if f["kind"] == "block"]
        assert block_paths
        block_from_manifest = json.loads(zf.read(block_paths[0]))
        assert block_from_manifest["block"]["id"] == block_id
        assert block_data["generation_rules"]["document_lexicon"]["labels"]["fascicle"] == "Capítulo"
        assert block_data["block"]["text_production_label_pt"] == "Ponto"
        assert block_data["fascicle"]["text_production_label_pt"] == "Capítulo"
        _validate_llm_export(master_data)
        _validate_llm_export(fascicle_data)
        _validate_llm_export(block_data)

        md_name = block_paths[0].replace("_llm.json", "_llm.md")
        assert md_name in names
        block_md = zf.read(md_name).decode("utf-8")
        assert "## Glossário" in block_md
        assert "## Capítulo" in block_md
        assert "## Fascículo" not in block_md
        assert "## Pontos de desenvolvimento" in block_md

        term_md_name = "terminology_discussion_llm.md"
        term_json_name = "terminology_discussion_llm.json"
        assert term_md_name in names
        assert term_json_name in names
        term_md = zf.read(term_md_name).decode("utf-8")
        assert "Glossário técnico" in term_md
        assert "Adjudicatário" in term_md
        term_json = json.loads(zf.read(term_json_name))
        assert term_json["get_export"]["schema"] == "GET-LLM-TERMINOLOGY"
        assert any(
            t.get("preferred_term") == "Adjudicatário"
            for t in term_json["payload"].get("library_terms") or []
        )

        master_md = zf.read(master_name.replace(".json", ".md")).decode("utf-8")
        assert term_json_name in master_md
        assert "Glossário técnico (vocabulário)" in master_md
        master_data = json.loads(zf.read(master_name))
        assert master_data.get("package_terminology_json") == term_json_name


def test_e06_roundtrip_still_requires_baseline(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    project = _project(client)
    pid = project["id"]
    no_baseline = client.post(f"/api/projects/{pid}/exports/master", json={"profile": "discussion"})
    assert no_baseline.status_code == 400