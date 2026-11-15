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