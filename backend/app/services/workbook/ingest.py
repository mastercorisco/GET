from __future__ import annotations

import uuid
from pathlib import Path

from app.config import AppSettings
from app.services.workspace_paths import WorkspacePaths
from app.services.workspace_service import WorkspaceError, workspace_session


class WorkbookIngestError(Exception):
    pass


def persist_workbook_upload(app_settings: AppSettings, raw: bytes, *, run_id: str | None = None) -> tuple[str, Path]:
    if not raw:
        raise WorkbookIngestError("Ficheiro vazio.")
    run_id = run_id or str(uuid.uuid4())
    try:
        with workspace_session(app_settings) as (_session, paths):
            paths.ensure_layout()
            dest = _import_path(paths, run_id)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            return run_id, dest
    except WorkspaceError as exc:
        raise WorkbookIngestError(str(exc)) from exc


def resolve_workbook_import(paths: WorkspacePaths, run_id: str) -> Path:
    path = _import_path(paths, run_id)
    if not path.is_file():
        raise WorkbookIngestError(f"Upload em falta para run_id {run_id}.")
    return path


def _import_path(paths: WorkspacePaths, run_id: str) -> Path:
    return paths.imports_dir / "workbook" / run_id / "source.xlsx"