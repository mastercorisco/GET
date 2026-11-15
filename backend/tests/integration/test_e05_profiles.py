from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.deps import get_settings
from app.main import app
from app.models.technical_profile import TechnicalProfilePayload
from app.services.workspace_service import workspace_session


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


def _item(client: TestClient) -> str:
    created = client.post(
        "/api/knowledge",
        json={"title": "Decisão", "content": "texto", "origin_context": "teste", "knowledge_type": "decision"},
    )
    assert created.status_code == 200
    return created.json()["id"]


def test_technical_profile_conclude_snapshots_two_revisions(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    item_id = _item(client)
    profile = client.patch(
        f"/api/knowledge/{item_id}/technical-profile",
        json={
            "profile_type": "decision",
            "data": {"decision_scope": "Feeders", "technical_parameters": "100%"},
        },
    )
    assert profile.status_code == 200
    assert profile.json()["profile_type"] == "decision"

    r1 = client.post(f"/api/knowledge/{item_id}/conclude")
    assert r1.status_code == 200

    client.patch(
        f"/api/knowledge/{item_id}/technical-profile",
        json={"profile_type": "decision", "data": {"decision_scope": "Outro"}},
    )
    r2 = client.post(f"/api/knowledge/{item_id}/conclude")
    assert r2.status_code == 200
    assert r2.json()["latest_revision_num"] == 2

    with workspace_session(get_settings()) as (session, _):
        payloads = list(session.scalars(select(TechnicalProfilePayload).order_by(TechnicalProfilePayload.id)))
        assert len(payloads) == 2
        assert payloads[0].data_json != payloads[1].data_json


def test_invalid_profile_type(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    item_id = _item(client)
    bad = client.patch(
        f"/api/knowledge/{item_id}/technical-profile",
        json={"profile_type": "not_a_type", "data": {}},
    )
    assert bad.status_code in (400, 422)