from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import AppSettings, get_active_workspace_root, set_active_workspace_root
from app.db.session import get_session_factory_for_workspace
from app.models.workspace import WorkspaceSettings
from app.schemas.workspace import WorkspaceResponse
from app.services.workspace_paths import WorkspacePaths


class WorkspaceError(Exception):
    pass


_migrated_databases: set[str] = set()


def _ensure_workspace_schema(db_path: Path) -> None:
    key = str(db_path.resolve())
    if key in _migrated_databases:
        return
    migrate_workspace_database(db_path)
    _migrated_databases.add(key)


def _to_response(settings: WorkspaceSettings, paths: WorkspacePaths) -> WorkspaceResponse:
    return WorkspaceResponse(
        id=settings.id,
        root_path=settings.root_path,
        local_user_name=settings.local_user_name,
        database_path=str(paths.database_path),
        backups_path=str(paths.backups_dir),
        exports_path=str(paths.exports_dir),
        imports_path=str(paths.imports_dir),
    )


def get_workspace_db_path(app_settings: AppSettings) -> Path:
    root = get_active_workspace_root(app_settings)
    if root is None:
        raise WorkspaceError("Nenhum workspace aberto.")
    return WorkspacePaths(root).database_path


def require_workspace_session(app_settings: AppSettings) -> tuple[Session, WorkspacePaths]:
    db_path = get_workspace_db_path(app_settings)
    _ensure_workspace_schema(db_path)
    _, factory = get_session_factory_for_workspace(db_path)
    root = get_active_workspace_root(app_settings)
    if root is None:
        raise WorkspaceError("Nenhum workspace aberto.")
    paths = WorkspacePaths(root)
    return factory(), paths


@contextmanager
def workspace_session(app_settings: AppSettings):
    session, paths = require_workspace_session(app_settings)
    try:
        yield session, paths
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def migrate_workspace_database(db_path: Path) -> None:
    """Apply Alembic migrations to the workspace database."""
    import sqlite3

    key = str(db_path.resolve())
    if key in _migrated_databases:
        return

    db_path.parent.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "GET_ALEMBIC_URL": f"sqlite:///{db_path.resolve()}",
    }
    backend = _backend_root()

    if db_path.exists():
        with sqlite3.connect(db_path) as conn:
            has_version = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='alembic_version'"
            ).fetchone()
            has_workspace = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='workspace_settings'"
            ).fetchone()
        if has_workspace and not has_version:
            stamp = subprocess.run(
                [sys.executable, "-m", "alembic", "stamp", "head"],
                cwd=backend,
                env=env,
                capture_output=True,
                text=True,
            )
            if stamp.returncode != 0:
                raise WorkspaceError(
                    f"Carimbo Alembic falhou: {stamp.stderr or stamp.stdout or 'erro desconhecido'}"
                )
            _migrated_databases.add(key)
            return

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise WorkspaceError(
            f"Migração Alembic falhou: {result.stderr or result.stdout or 'erro desconhecido'}"
        )
    _migrated_databases.add(key)


def get_current_workspace(app_settings: AppSettings) -> WorkspaceResponse | None:
    root = get_active_workspace_root(app_settings)
    if root is None:
        return None
    paths = WorkspacePaths(root)
    if not paths.database_path.exists():
        return None
    _, factory = get_session_factory_for_workspace(paths.database_path)
    with factory() as session:
        settings = session.scalar(select(WorkspaceSettings).limit(1))
        if settings is None:
            return None
        return _to_response(settings, paths)


def create_workspace(
    app_settings: AppSettings,
    root_path: str,
    local_user_name: str,
) -> WorkspaceResponse:
    root = Path(root_path).expanduser().resolve()
    paths = WorkspacePaths(root)
    paths.ensure_layout()

    migrate_workspace_database(paths.database_path)

    _, factory = get_session_factory_for_workspace(paths.database_path)
    with factory() as session:
        existing = session.scalar(
            select(WorkspaceSettings).where(WorkspaceSettings.root_path == str(root))
        )
        if existing:
            set_active_workspace_root(app_settings, root)
            return _to_response(existing, paths)

        settings = WorkspaceSettings(
            root_path=str(root),
            local_user_name=local_user_name,
            schema_versions_json=json.dumps({"app": "0.1.0", "json_schema": "1.0.0"}),
        )
        session.add(settings)
        session.commit()
        session.refresh(settings)
        response = _to_response(settings, paths)

    set_active_workspace_root(app_settings, root)
    return response


def open_workspace(app_settings: AppSettings, root_path: str) -> WorkspaceResponse:
    root = Path(root_path).expanduser().resolve()
    paths = WorkspacePaths(root)
    if not paths.database_path.exists():
        raise WorkspaceError(f"Workspace inválido: base de dados em falta em {paths.database_path}")

    migrate_workspace_database(paths.database_path)

    _, factory = get_session_factory_for_workspace(paths.database_path)
    with factory() as session:
        settings = session.scalar(select(WorkspaceSettings).where(WorkspaceSettings.root_path == str(root)))
        if settings is None:
            raise WorkspaceError("Workspace sem registo de configuração.")
        response = _to_response(settings, paths)

    set_active_workspace_root(app_settings, root)
    return response