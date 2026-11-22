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


def test_terminology_and_project_override(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post("/api/knowledge", json={"title": "s", "content": "c", "origin_context": "t"})
    concept = client.post(
        "/api/terminology",
        json={
            "scope_type": "library",
            "preferred_term": "Feeder",
            "definition": "Linha de alimentação de combustível.",
            "synonyms": ["alimentador", "feeder line"],
        },
    )
    assert concept.status_code == 200
    concept_id = concept.json()["id"]
    assert concept.json()["synonyms"] == ["alimentador", "feeder line"]

    templates = client.get("/api/projects/templates").json()
    v1 = templates[0]["versions"][0]["id"]
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P", "intervention_type": "brownfield"},
    ).json()

    override = client.post(
        f"/api/projects/{project['id']}/terminology-overrides",
        json={"concept_id": concept_id, "legacy_term": "Alimentador combustível", "usage_note": "Histórico"},
    )
    assert override.status_code == 200
    assert override.json()["legacy_term"] == "Alimentador combustível"

    listed = client.get(f"/api/projects/{project['id']}/terminology-overrides")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_terminology_patch_library(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    concept = client.post(
        "/api/terminology",
        json={
            "scope_type": "library",
            "preferred_term": "Antes",
            "definition": "Definição original.",
            "synonyms": ["a"],
        },
    )
    assert concept.status_code == 200
    concept_id = concept.json()["id"]
    updated = client.patch(
        f"/api/terminology/{concept_id}",
        json={
            "preferred_term": "Depois",
            "definition": "Definição actualizada.",
            "synonyms": ["b", "c"],
        },
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["preferred_term"] == "Depois"
    assert body["definition"] == "Definição actualizada."
    assert body["synonyms"] == ["b", "c"]


def test_terminology_search_library_and_project(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post("/api/knowledge", json={"title": "s", "content": "c", "origin_context": "t"})
    concept = client.post(
        "/api/terminology",
        json={
            "scope_type": "library",
            "preferred_term": "Feeder",
            "definition": "Linha de alimentação de combustível.",
            "synonyms": ["alimentador", "feeder line"],
        },
    ).json()
    templates = client.get("/api/projects/templates").json()
    v1 = templates[0]["versions"][0]["id"]
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P", "intervention_type": "brownfield"},
    ).json()
    client.post(
        f"/api/projects/{project['id']}/terminology-overrides",
        json={"concept_id": concept["id"], "legacy_term": "Alimentador combustível"},
    )

    by_synonym = client.get("/api/terminology/search", params={"q": "alimentador"})
    assert by_synonym.status_code == 200
    assert len(by_synonym.json()) == 1
    assert by_synonym.json()[0]["concept"]["preferred_term"] == "Feeder"

    merged = client.get(
        "/api/terminology/search",
        params={"q": "combustível", "project_id": project["id"]},
    )
    assert merged.status_code == 200
    assert len(merged.json()) == 1
    assert merged.json()[0]["project_override"]["legacy_term"] == "Alimentador combustível"

    empty = client.get("/api/terminology/search", params={"q": "   "})
    assert empty.status_code == 400


def test_terminology_delete_requires_confirm(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post("/api/knowledge", json={"title": "s", "content": "c", "origin_context": "t"})
    concept = client.post(
        "/api/terminology",
        json={
            "scope_type": "library",
            "preferred_term": "Apagar-me",
            "definition": "Teste confirm.",
        },
    ).json()
    cid = concept["id"]
    blocked = client.delete(f"/api/terminology/{cid}")
    assert blocked.status_code == 400
    assert client.get("/api/terminology", params={"scope_type": "library"}).json()
    ok = client.delete(f"/api/terminology/{cid}", params={"confirm": True})
    assert ok.status_code == 204
    assert client.delete(f"/api/terminology/{cid}", params={"confirm": True}).status_code == 400


def test_terminology_override_delete_requires_confirm(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    client.post("/api/knowledge", json={"title": "s", "content": "c", "origin_context": "t"})
    concept = client.post(
        "/api/terminology",
        json={"scope_type": "library", "preferred_term": "X", "definition": "d"},
    ).json()
    templates = client.get("/api/projects/templates").json()
    v1 = templates[0]["versions"][0]["id"]
    project = client.post(
        "/api/projects",
        json={"template_version_id": v1, "name": "P", "intervention_type": "brownfield"},
    ).json()
    pid = project["id"]
    ov = client.post(
        f"/api/projects/{pid}/terminology-overrides",
        json={"concept_id": concept["id"], "legacy_term": "Legado"},
    ).json()
    oid = ov["id"]
    assert client.delete(f"/api/projects/{pid}/terminology-overrides/{oid}").status_code == 400
    assert client.delete(f"/api/projects/{pid}/terminology-overrides/{oid}", params={"confirm": True}).status_code == 204