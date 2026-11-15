from __future__ import annotations

from pathlib import Path

from app.config import AppSettings
from app.services.workbook.apply import WorkbookApplyError, apply_workbook_bundle
from app.services.workbook.constants import CONFIRM_PHRASE
from app.services.workbook.extract import extract_workbook
from app.services.workbook.stage import write_migration_report
from app.services.workbook.types import MigrationRunResult
from app.services.workspace_paths import WorkspacePaths
from app.services.workspace_service import WorkspaceError, workspace_session


class WorkbookMigrationError(Exception):
    pass


def run_workbook_migration(
    app_settings: AppSettings,
    workbook_path: Path,
    *,
    dry_run: bool = True,
    confirm: str | None = None,
) -> MigrationRunResult:
    workbook_path = workbook_path.resolve()
    if not workbook_path.is_file():
        raise WorkbookMigrationError(f"Workbook não encontrado: {workbook_path}")

    bundle, issues = extract_workbook(workbook_path)
    if bundle is None:
        blocking = sum(1 for i in issues if i.severity == "error")
        raise WorkbookMigrationError(f"Extração falhou com {blocking} erro(s) bloqueante(s).")

    try:
        with workspace_session(app_settings) as (_session, paths):
            paths.ensure_layout()
            report_path = write_migration_report(
                paths.migration_reports_dir,
                bundle,
                issues,
                mode="dry-run" if dry_run else "apply",
            )
            run_id = report_path.parent.name
    except WorkspaceError as exc:
        raise WorkbookMigrationError(str(exc)) from exc

    blocking = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")

    if blocking:
        return MigrationRunResult(
            run_id=run_id,
            report_path=str(report_path),
            blocking_errors=blocking,
            warnings=warnings,
            applied=False,
        )

    if dry_run:
        return MigrationRunResult(
            run_id=run_id,
            report_path=str(report_path),
            blocking_errors=0,
            warnings=warnings,
            applied=False,
        )

    if confirm != CONFIRM_PHRASE:
        raise WorkbookMigrationError(
            f"Aplicação requer --confirm {CONFIRM_PHRASE} após rever report.json."
        )

    try:
        project_id = apply_workbook_bundle(app_settings, bundle)
    except WorkbookApplyError as exc:
        raise WorkbookMigrationError(str(exc)) from exc

    return MigrationRunResult(
        run_id=run_id,
        report_path=str(report_path),
        blocking_errors=0,
        warnings=warnings,
        applied=True,
        project_id=project_id,
    )