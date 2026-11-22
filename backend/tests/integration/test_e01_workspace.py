from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import AppSettings, get_active_workspace_root
from app.deps import get_settings
from app.main import app
from app.services.workspace_exclusivity import workspace_exclusive
from app.services.workspace_service import migrate_workspace_database


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


def test_health_workspace_without_open_workspace(client: TestClient) -> None:
    response = client.get("/api/health/workspace")
    assert response.status_code == 409


def test_health_workspace_ok(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "ws-health"
    client.post(
        "/api/workspace/create",
        json={"root_path": str(ws), "local_user_name": "tester"},
    )
    response = client.get("/api/health/workspace")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["integrity"] == "ok"
    assert "journal_mode" in body


def test_env_workspace_root_used_by_health(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ws = tmp_path / "ws-env"
    ws.mkdir()
    (ws / "data").mkdir(parents=True)
    cfg = tmp_path / "app-config.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    monkeypatch.setenv("GET_WORKSPACE_ROOT", str(ws))
    get_settings.cache_clear()
    client.post(
        "/api/workspace/create",
        json={"root_path": str(ws), "local_user_name": "env"},
    )
    assert get_active_workspace_root(get_settings()) == ws.resolve()
    response = client.get("/api/health/workspace")
    assert response.status_code == 200
    assert response.json()["workspace_root"] == str(ws.resolve())


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

    backup = client.post(
        "/api/backups",
        json={"tier": "critical", "user_note": "  Antes do teste  "},
    )
    assert backup.status_code == 200
    assert backup.json()["user_note"] == "Antes do teste"
    assert Path(backup.json()["file_path"]).exists()

    listing = client.get("/api/backups")
    assert listing.status_code == 200
    assert len(listing.json()) >= 1

    backup_id = listing.json()[0]["id"]
    preview = client.get(f"/api/backups/{backup_id}/preview")
    assert preview.status_code == 200
    assert preview.json()["workspace_settings_rows"] == 1

    file_path = Path(backup.json()["file_path"])
    assert client.post(f"/api/backups/{backup_id}/discard").status_code == 204
    assert not file_path.exists()
    listing_after = client.get("/api/backups")
    assert backup_id not in {row["id"] for row in listing_after.json()}
    assert client.get(f"/api/backups/{backup_id}/preview").status_code == 404
    assert client.post(f"/api/backups/{backup_id}/discard").status_code == 404


def test_bind_host_defaults_localhost() -> None:
    settings = AppSettings()
    assert settings.host == "127.0.0.1"


def test_migrate_reconciles_stale_alembic_version(tmp_path: Path) -> None:
    backend = Path(__file__).resolve().parents[2]
    db = tmp_path / "data" / "get.db"
    db.parent.mkdir(parents=True)
    env = {**os.environ, "GET_ALEMBIC_URL": f"sqlite:///{db.resolve()}"}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "006"],
        cwd=backend,
        env=env,
        check=True,
    )
    with sqlite3.connect(db) as conn:
        conn.execute("UPDATE alembic_version SET version_num = '005'")
        conn.commit()
    migrate_workspace_database(db)
    with sqlite3.connect(db) as conn:
        version = conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    assert version == "009"
    assert {row[0] for row in sqlite3.connect(db).execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}.__contains__("import_record")


def test_restore_blocked_while_exclusive_operation(client: TestClient, tmp_path: Path) -> None:
    ws = tmp_path / "workspace-exclusive"
    client.post(
        "/api/workspace/create",
        json={"root_path": str(ws), "local_user_name": "tester"},
    )
    backup = client.post("/api/backups", json={"tier": "critical"})
    backup_id = backup.json()["id"]
    with workspace_exclusive("test_hold"):
        denied = client.post(f"/api/backups/{backup_id}/restore", params={"confirm": "true"})
    assert denied.status_code == 409
    assert "workspace" in denied.json()["detail"].lower()


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