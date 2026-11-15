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
    response = client.post(
        "/api/workspace/create",
        json={"root_path": str(tmp_path / "workspace"), "local_user_name": "tester"},
    )
    assert response.status_code == 200


def _create(client: TestClient, title: str, content: str = "conteúdo mínimo") -> dict:
    response = client.post(
        "/api/knowledge",
        json={
            "title": title,
            "content": content,
            "origin_context": "ensaio de bancada",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["status_label"] == "rascunho"
    assert body["revision_count"] == 0
    assert body["scope_type"] == "library"
    return body


def test_draft_is_separate_from_revision(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    created = _create(client, "Unidade inicial")

    updated = client.patch(
        f"/api/knowledge/{created['id']}/draft",
        json={
            "title": "Unidade editada",
            "content": "texto novo",
            "origin_context": "ensaio de bancada",
        },
    )
    assert updated.status_code == 200
    body = updated.json()
    assert body["title"] == "Unidade editada"
    assert body["revision_count"] == 0
    assert body["revisions"] == []


def test_revisions_are_append_only(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    created = _create(client, "Título um", "primeiro conteúdo")
    first = client.post(f"/api/knowledge/{created['id']}/conclude")
    assert first.status_code == 200
    assert first.json()["revisions"][0]["title"] == "Título um"
    assert first.json()["status_label"].startswith("revisão 1")

    edited = client.patch(
        f"/api/knowledge/{created['id']}/draft",
        json={
            "title": "Título dois",
            "content": "segundo conteúdo",
            "origin_context": "ensaio de bancada",
        },
    )
    assert edited.status_code == 200
    second = client.post(f"/api/knowledge/{created['id']}/conclude")
    assert second.status_code == 200
    revisions = second.json()["revisions"]
    assert [item["revision_num"] for item in revisions] == [1, 2]
    assert revisions[0]["title"] == "Título um"
    assert revisions[0]["content"] == "primeiro conteúdo"
    assert revisions[1]["title"] == "Título dois"


def test_self_relation_is_rejected(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    created = _create(client, "Sem auto-relação")
    denied = client.post(
        "/api/knowledge/relations",
        json={
            "source_item_id": created["id"],
            "target_item_id": created["id"],
            "relation_type": "depends_on",
        },
    )
    assert denied.status_code == 400

    other = _create(client, "Outra unidade")
    allowed = client.post(
        "/api/knowledge/relations",
        json={
            "source_item_id": created["id"],
            "target_item_id": other["id"],
            "relation_type": "related_to",
        },
    )
    assert allowed.status_code == 200
    assert allowed.json()["relation_type"] == "related_to"


def test_search_returns_library_title(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _create(client, "Bombagem de fuelóleo", "circuito de alimentação")
    _create(client, "Ventilação da casa das máquinas")

    found = client.get("/api/knowledge/search", params={"q": "fuelóleo", "scope_type": "library"})
    assert found.status_code == 200
    titles = [item["title"] for item in found.json()]
    assert titles == ["Bombagem de fuelóleo"]
    assert found.json()[0]["scope_type"] == "library"
