from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import select, text
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


def _active_root(app_settings: AppSettings) -> Path | None:
    try:
        return get_active_workspace_root(app_settings)
    except ValueError as exc:
        raise WorkspaceError(str(exc)) from exc


def get_workspace_db_path(app_settings: AppSettings) -> Path:
    root = _active_root(app_settings)
    if root is None:
        raise WorkspaceError("Nenhum workspace aberto.")
    return WorkspacePaths(root).database_path


def workspace_preflight(app_settings: AppSettings) -> dict:
    root = _active_root(app_settings)
    if root is None:
        raise WorkspaceError("Nenhum workspace aberto.")
    paths = WorkspacePaths(root)
    paths.ensure_layout()
    db = paths.database_path
    if not db.is_file():
        return {
            "ok": False,
            "reason": "database_missing",
            "workspace_root": str(root),
            "database_path": str(db),
        }
    with sqlite3.connect(db) as conn:
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        journal_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    return {
        "ok": integrity == "ok",
        "workspace_root": str(root),
        "database_path": str(db),
        "integrity": integrity,
        "journal_mode": journal_mode,
    }


def require_workspace_session(app_settings: AppSettings) -> tuple[Session, WorkspacePaths]:
    db_path = get_workspace_db_path(app_settings)
    _ensure_workspace_schema(db_path)
    _, factory = get_session_factory_for_workspace(db_path)
    root = _active_root(app_settings)
    if root is None:
        raise WorkspaceError("Nenhum workspace aberto.")
    paths = WorkspacePaths(root)
    return factory(), paths


@contextmanager
def workspace_session(app_settings: AppSettings, *, begin_immediate: bool = False):
    session, paths = require_workspace_session(app_settings)
    try:
        if begin_immediate:
            session.execute(text("BEGIN IMMEDIATE"))
        yield session, paths
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _revision_num(rev: str) -> int:
    return int(rev)


def _table_names(conn) -> set[str]:
    import sqlite3

    if not isinstance(conn, sqlite3.Connection):
        raise TypeError("expected sqlite3.Connection")
    return {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _read_alembic_version(conn) -> str | None:
    import sqlite3

    if "alembic_version" not in _table_names(conn):
        return None
    row = conn.execute("SELECT version_num FROM alembic_version").fetchone()
    return row[0] if row else None


def _inferred_schema_revision(conn) -> str | None:
    names = _table_names(conn)
    if "import_record" in names:
        return "007"
    if "baseline" in names and "export_record" in names:
        return "006"
    return None


def _stamp_alembic(db_path: Path, revision: str) -> None:
    env = {
        **os.environ,
        "GET_ALEMBIC_URL": f"sqlite:///{db_path.resolve()}",
    }
    backend = _backend_root()
    stamp = subprocess.run(
        [sys.executable, "-m", "alembic", "stamp", revision],
        cwd=backend,
        env=env,
        capture_output=True,
        text=True,
    )
    if stamp.returncode != 0:
        raise WorkspaceError(
            f"Carimbo Alembic ({revision}) falhou: {stamp.stderr or stamp.stdout or 'erro desconhecido'}"
        )


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
            recorded = _read_alembic_version(conn)
            inferred = _inferred_schema_revision(conn)
        if has_workspace and not has_version:
            _stamp_alembic(db_path, "head")
            _migrated_databases.add(key)
            return
        if recorded and inferred and _revision_num(inferred) > _revision_num(recorded):
            _stamp_alembic(db_path, inferred)
        elif recorded and _revision_num(recorded) < 6:
            with sqlite3.connect(db_path) as conn:
                names = _table_names(conn)
            if "baseline" in names and "export_record" not in names:
                raise WorkspaceError(
                    "Schema E06 incompleto (existe baseline, falta export_record). "
                    "Restaure um backup crítico ou crie um workspace novo."
                )

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
    root = _active_root(app_settings)
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