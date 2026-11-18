from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.deps import get_settings
from app.domain.block.models import DevelopmentPoint
from app.main import app
from app.models.document import DocumentNode
from app.services.structure_seed.ctbj_v3_sync import EXPECTED_BLOCKS, EXPECTED_FASCICLES, apply_ctbj_v3_structure
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


def _template_v2(client: TestClient) -> str:
    templates = client.get("/api/projects/templates")
    assert templates.status_code == 200
    versions = templates.json()[0]["versions"]
    v2 = next(v for v in versions if v["version"] == 2)
    return v2["id"]


def test_create_project_v2_seeds_ctbj_structure(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v2_id = _template_v2(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v2_id,
            "name": "CTBJ teste seed",
            "intervention_type": "brownfield",
        },
    )
    assert created.status_code == 200
    project_id = created.json()["id"]

    settings = get_settings()
    with workspace_session(settings) as (session, _paths):
        fascicles = session.scalar(
            select(func.count())
            .select_from(DocumentNode)
            .where(DocumentNode.project_id == project_id, DocumentNode.node_type == "fascicle")
        )
        blocks = session.scalar(
            select(func.count())
            .select_from(DocumentNode)
            .where(DocumentNode.project_id == project_id, DocumentNode.node_type == "block")
        )
        points = session.scalar(select(func.count()).select_from(DevelopmentPoint))
    assert fascicles == EXPECTED_FASCICLES
    assert blocks == EXPECTED_BLOCKS
    assert points >= 869


def test_ctbj_sync_idempotent_skip(client: TestClient, tmp_path: Path) -> None:
    _workspace(client, tmp_path)
    _ensure_library(client)
    v2_id = _template_v2(client)
    created = client.post(
        "/api/projects",
        json={
            "template_version_id": v2_id,
            "name": "CTBJ idempotência",
            "intervention_type": "brownfield",
        },
    )
    project_id = created.json()["id"]
    settings = get_settings()
    repeat = apply_ctbj_v3_structure(settings, project_id, mode="migrate", dry_run=False)
    again = apply_ctbj_v3_structure(settings, project_id, mode="migrate", dry_run=False)
    assert repeat.skipped is True
    assert again.skipped is True