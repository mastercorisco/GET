from __future__ import annotations

from datetime import datetime, timezone

from app.config import AppSettings
from app.services.workbook.export_builder import (
    build_workbook_export_library,
    build_workbook_export_project,
    persist_workbook_export,
)
from app.services.workspace_service import WorkspaceError


class WorkbookExportError(Exception):
    pass


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def export_workbook_library(app_settings: AppSettings) -> tuple[bytes, str, str]:
    try:
        data = build_workbook_export_library(app_settings)
        filename = f"library_export_{_timestamp()}.xlsx"
        path = persist_workbook_export(app_settings, data, filename)
        return data, filename, path
    except WorkspaceError as exc:
        raise WorkbookExportError(str(exc)) from exc
    except ValueError as exc:
        raise WorkbookExportError(str(exc)) from exc


def export_workbook_project(app_settings: AppSettings, project_id: str) -> tuple[bytes, str, str]:
    try:
        data = build_workbook_export_project(app_settings, project_id)
        filename = f"project_{project_id[:8]}_export_{_timestamp()}.xlsx"
        path = persist_workbook_export(app_settings, data, filename)
        return data, filename, path
    except WorkspaceError as exc:
        raise WorkbookExportError(str(exc)) from exc
    except ValueError as exc:
        raise WorkbookExportError(str(exc)) from exc