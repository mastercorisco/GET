from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from app.config import AppSettings
from app.schemas.workbook import WorkbookApplyResponse, WorkbookMigrateResponse
from app.services.workbook.apply import (
    WorkbookApplyError,
    apply_workbook_bundle,
    apply_workbook_to_project,
)
from app.services.workbook.constants import CONFIRM_PHRASE
from app.services.workbook.extract import extract_workbook
from app.services.workbook.ingest import WorkbookIngestError, persist_workbook_upload
from app.services.workbook.migrate import WorkbookMigrationError, run_workbook_migration
from app.services.workspace_exclusivity import WorkspaceExclusiveError, workspace_exclusive
from app.services.workspace_service import WorkspaceError, workspace_session


class WorkbookApiError(Exception):
    def __init__(self, message: str, *, http_status: int = 400) -> None:
        super().__init__(message)
        self.http_status = http_status


def _report_to_migrate_response(report: dict[str, Any], report_path: str) -> WorkbookMigrateResponse:
    status = report.get("status", "blocked")
    if status not in ("ready", "blocked"):
        status = "blocked" if report.get("blocking_errors", 0) else "ready"
    return WorkbookMigrateResponse(
        run_id=report["run_id"],
        status=status,  # type: ignore[arg-type]
        blocking_errors=int(report.get("blocking_errors", 0)),
        warnings=int(report.get("warnings", 0)),
        counts=dict(report.get("counts") or {}),
        issues=list(report.get("issues") or []),
        preview=report.get("preview"),
        report_path=report_path,
    )


def migrate_workbook_upload(
    app_settings: AppSettings,
    raw: bytes,
    filename: str,
    *,
    dry_run: bool = True,
    compare_project_id: str | None = None,
) -> WorkbookMigrateResponse:
    _ = filename
    try:
        run_id, path = persist_workbook_upload(app_settings, raw)
    except WorkbookIngestError as exc:
        raise WorkbookApiError(str(exc)) from exc

    try:
        result = run_workbook_migration(
            app_settings,
            path,
            dry_run=dry_run,
            run_id=run_id,
            compare_project_id=compare_project_id,
        )
    except WorkbookMigrationError as exc:
        raise WorkbookApiError(str(exc)) from exc

    report = load_migration_report(app_settings, result.run_id)
    return _report_to_migrate_response(report, result.report_path)


def load_migration_report(app_settings: AppSettings, run_id: str) -> dict[str, Any]:
    try:
        with workspace_session(app_settings) as (_session, paths):
            report_path = paths.migration_reports_dir / run_id / "report.json"
            if not report_path.is_file():
                raise WorkbookApiError("Relatório de migração não encontrado.", http_status=404)
            return json.loads(report_path.read_text(encoding="utf-8"))
    except WorkspaceError as exc:
        raise WorkbookApiError(str(exc), http_status=409) from exc


def apply_workbook_migration(
    app_settings: AppSettings,
    run_id: str,
    *,
    confirm: str,
    target: Literal["new_project", "existing_project"],
    project_id: str | None = None,
) -> WorkbookApplyResponse:
    if confirm != CONFIRM_PHRASE:
        raise WorkbookApiError(
            f"Confirmação inválida. Utilize exactamente: {CONFIRM_PHRASE}.",
        )

    report = load_migration_report(app_settings, run_id)
    if report.get("status") != "ready":
        raise WorkbookApiError(
            "Relatório bloqueado ou inválido; corrija erros e volte a executar o dry-run.",
            http_status=422,
        )

    workbook_path = Path(report["workbook_path"])
    if not workbook_path.is_file():
        raise WorkbookApiError(
            "Ficheiro do dry-run em falta; volte a carregar o Excel antes de consolidar.",
        )

    bundle, issues = extract_workbook(workbook_path)
    if bundle is None:
        blocking = sum(1 for i in issues if i.severity == "error")
        raise WorkbookApiError(f"Extração falhou com {blocking} erro(s).", http_status=422)

    blocking = sum(1 for i in issues if i.severity == "error")
    if blocking:
        raise WorkbookApiError("Workbook com erros bloqueantes.", http_status=422)

    try:
        with workspace_exclusive("workbook_apply"):
            if target == "new_project":
                result_project_id = apply_workbook_bundle(app_settings, bundle)
                summary = _summary_from_counts(report.get("counts"))
            else:
                if not project_id:
                    raise WorkbookApiError("project_id é obrigatório para projecto existente.")
                result_project_id, summary = apply_workbook_to_project(
                    app_settings, project_id, bundle
                )
    except WorkspaceExclusiveError as exc:
        raise WorkbookApiError(str(exc), http_status=409) from exc
    except WorkbookApplyError as exc:
        raise WorkbookApiError(str(exc), http_status=422) from exc

    _mark_report_applied(app_settings, run_id, target, result_project_id)

    return WorkbookApplyResponse(
        run_id=run_id,
        project_id=result_project_id,
        target=target,
        applied=True,
        summary=summary,
    )


def _summary_from_counts(counts: Any) -> dict[str, int] | None:
    if not isinstance(counts, dict):
        return None
    return {k: int(v) for k, v in counts.items() if isinstance(v, (int, float))}


def _mark_report_applied(
    app_settings: AppSettings,
    run_id: str,
    target: str,
    project_id: str,
) -> None:
    try:
        with workspace_session(app_settings) as (_session, paths):
            report_path = paths.migration_reports_dir / run_id / "report.json"
            if not report_path.is_file():
                return
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["mode"] = "apply"
            report["applied_target"] = target
            report["applied_project_id"] = project_id
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
    except WorkspaceError:
        pass