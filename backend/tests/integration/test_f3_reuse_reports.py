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


def _block_with_two_points(client: TestClient, project_id: str) -> tuple[str, list[str]]:
    fascicle = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": "fascicle", "title": "Fasc", "parent_id": None},
    ).json()["node"]
    block = client.post(
        f"/api/projects/{project_id}/document-nodes",
        json={"node_type": "block", "title": "Bloco", "parent_id": fascicle["id"]},
    ).json()["node"]
    block_id = block["id"]
    client.patch(
        f"/api/blocks/{block_id}",
        json={"objective": "Obj", "scope": "Âmbito", "target_output": {"format": "spec_section"}},
    )
    point_ids: list[str] = []
    for title in ("P1", "P2"):
        pid = client.post(
            f"/api/blocks/{block_id}/development-points",
            json={"title": title, "template_id": "failure_behavior"},
        ).json()["id"]
        point_ids.append(pid)
        client.patch(
            f"/api/development-points/{pid}",
            json={
                "core_idea": "Ideia.",
                "lists": {
                    "development_guidance": [],
                    "perspectives": ["operational"],
                    "questions_to_answer": [],
                    "must_include": [],
                    "limits_and_exclusions": [],
                    "examples": [],
                    "open_questions": [],
                    "acceptance_criteria": [],
                    "knowledge_item_ids": [],
                    "reference_ids": [],
                },
                "status": "draft",
            },
        )
    return block_id, point_ids


def test_project_reuse_report_api_empty(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "Reuse API", "intervention_type": "brownfield"},
    ).json()
    resp = client.get(f"/api/projects/{project['id']}/reuse-report")
    assert resp.status_code == 200
    body = resp.json()
    assert body["project_id"] == project["id"]
    assert body["f3_pilot_ready"] is False
    assert body["m3_reuse_ready"] is False
    assert body["decisions"]["decision_count"] == 0


def test_reuse_report_two_point_citations(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v1 = _template_v1(client)
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "Reuse cite", "intervention_type": "brownfield"},
    ).json()
    pid = project["id"]
    block_id, point_ids = _block_with_two_points(client, pid)

    decision = client.post(
        "/api/knowledge",
        json={
            "title": "Decisão piloto",
            "content": "Fica fixado X.",
            "origin_context": "teste",
            "knowledge_type": "decision",
            "scope_type": "library",
        },
    )
    assert decision.status_code == 200
    kid = decision.json()["id"]

    ref = client.post(
        "/api/references",
        json={
            "scope_type": "project",
            "scope_id": pid,
            "title": "Norma partilhada",
            "citation": "NP 1234",
        },
    )
    assert ref.status_code == 200
    rid = ref.json()["id"]

    lists_patch = {
        "development_guidance": [],
        "perspectives": ["operational"],
        "questions_to_answer": [],
        "must_include": [],
        "limits_and_exclusions": [],
        "examples": [],
        "open_questions": [],
        "acceptance_criteria": [],
        "knowledge_item_ids": [kid],
        "reference_ids": [rid],
    }
    for point_id in point_ids:
        client.patch(
            f"/api/development-points/{point_id}",
            json={"lists": lists_patch},
        )

    report = client.get(f"/api/projects/{pid}/reuse-report").json()
    assert report["f3_pilot_ready"] is True
    assert report["m3_reuse_ready"] is True
    assert report["reuse_pilot_ready"] is True
    assert report["decisions"]["f3_criterion_met_count"] == 1
    assert report["references"]["m3_criterion_met_count"] == 1