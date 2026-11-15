from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

from app.config import AppSettings
from app.models.backup import BackupRecord
from app.models.workspace import WorkspaceSettings
from app.schemas.backup import BackupRecordResponse, BackupRestorePreviewResponse
from app.services.workspace_paths import WorkspacePaths
from app.services.workspace_service import WorkspaceError, get_workspace_db_path, workspace_session


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _backup_db(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(source) as src, sqlite3.connect(dest) as dst:
        src.execute("PRAGMA wal_checkpoint(FULL)")
        src.backup(dst)


def _count_preview(db_path: Path) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        ws = conn.execute("SELECT COUNT(*) FROM workspace_settings").fetchone()[0]
        br = conn.execute("SELECT COUNT(*) FROM backup_record").fetchone()[0]
    return {"workspace_settings_rows": ws, "backup_record_rows": br}


def _apply_retention(session, paths: WorkspacePaths, settings: WorkspaceSettings) -> None:
    for tier, limit in (
        ("critical", settings.retention_critical),
        ("daily", settings.retention_daily),
        ("weekly", settings.retention_weekly),
    ):
        records = session.scalars(
            select(BackupRecord)
            .where(BackupRecord.tier == tier)
            .order_by(BackupRecord.created_at.desc())
        ).all()
        for stale in records[limit:]:
            Path(stale.file_path).unlink(missing_ok=True)
            session.delete(stale)


def create_backup(app_settings: AppSettings, tier: str) -> BackupRecordResponse:
    db_path = get_workspace_db_path(app_settings)
    with workspace_session(app_settings) as (session, paths):
        settings = session.scalar(select(WorkspaceSettings).limit(1))
        if settings is None:
            raise WorkspaceError("Workspace sem configuração.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_file = paths.backups_dir / tier / f"get_{tier}_{timestamp}.db"
        _backup_db(db_path, backup_file)
        preview = _count_preview(backup_file)

        record = BackupRecord(
            tier=tier,
            file_path=str(backup_file),
            sha256=_sha256(backup_file),
            preview_meta_json=json.dumps(preview, sort_keys=True),
        )
        session.add(record)
        session.flush()
        session.refresh(record)
        _apply_retention(session, paths, settings)

        return BackupRecordResponse(
            id=record.id,
            tier=record.tier,
            file_path=record.file_path,
            sha256=record.sha256,
            created_at=record.created_at,
            preview_meta_json=preview,
        )


def list_backups(app_settings: AppSettings) -> list[BackupRecordResponse]:
    with workspace_session(app_settings) as (session, _):
        rows = session.scalars(select(BackupRecord).order_by(BackupRecord.created_at.desc())).all()
        return [
            BackupRecordResponse(
                id=row.id,
                tier=row.tier,
                file_path=row.file_path,
                sha256=row.sha256,
                created_at=row.created_at,
                preview_meta_json=json.loads(row.preview_meta_json or "{}"),
            )
            for row in rows
        ]


def restore_preview(app_settings: AppSettings, backup_id: str) -> BackupRestorePreviewResponse:
    with workspace_session(app_settings) as (session, _):
        record = session.get(BackupRecord, backup_id)
        if record is None:
            raise WorkspaceError("Backup não encontrado.")
        file_path = record.file_path
    meta = _count_preview(Path(file_path))
    return BackupRestorePreviewResponse(
        backup_id=backup_id,
        workspace_settings_rows=meta["workspace_settings_rows"],
        backup_record_rows=meta["backup_record_rows"],
        file_path=file_path,
    )


def restore_backup(app_settings: AppSettings, backup_id: str, *, confirm: bool) -> None:
    if not confirm:
        raise WorkspaceError("Confirmação obrigatória para restauro.")

    db_path = get_workspace_db_path(app_settings)
    backup_path: Path

    with workspace_session(app_settings) as (session, paths):
        record = session.get(BackupRecord, backup_id)
        if record is None:
            raise WorkspaceError("Backup não encontrado.")
        backup_path = Path(record.file_path)
        pre_critical = paths.backups_dir / "critical" / f"pre_restore_guard_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.db"
        _backup_db(db_path, pre_critical)

    if not backup_path.exists():
        raise WorkspaceError("Ficheiro de backup em falta.")

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA wal_checkpoint(FULL)")
    shutil.copy2(backup_path, db_path)