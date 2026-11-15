from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import AppSettings
from app.deps import get_settings
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    get_settings.cache_clear()
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_open_workspace_and_backup(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "workspace"
    create = client.post(
        "/api/workspace/create",
        json={"root_path": str(ws), "local_user_name": "tester"},
    )
    assert create.status_code == 200
    body = create.json()
    assert Path(body["database_path"]).exists()

    current = client.get("/api/workspace")
    assert current.status_code == 200
    assert current.json()["local_user_name"] == "tester"

    backup = client.post("/api/backups", json={"tier": "critical"})
    assert backup.status_code == 200
    assert Path(backup.json()["file_path"]).exists()

    listing = client.get("/api/backups")
    assert listing.status_code == 200
    assert len(listing.json()) >= 1

    backup_id = listing.json()[0]["id"]
    preview = client.get(f"/api/backups/{backup_id}/preview")
    assert preview.status_code == 200
    assert preview.json()["workspace_settings_rows"] == 1


def test_bind_host_defaults_localhost() -> None:
    settings = AppSettings()
    assert settings.host == "127.0.0.1"


def test_restore_requires_confirm(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "workspace-restore"
    client.post(
        "/api/workspace/create",
        json={"root_path": str(ws), "local_user_name": "tester"},
    )
    backup = client.post("/api/backups", json={"tier": "critical"})
    backup_id = backup.json()["id"]
    denied = client.post(f"/api/backups/{backup_id}/restore", params={"confirm": "false"})
    assert denied.status_code == 400