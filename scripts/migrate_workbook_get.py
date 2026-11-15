#!/usr/bin/env python3
"""Migração dedicada do workbook GET (E08)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND = REPO_ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.config import AppSettings, get_active_workspace_root, set_active_workspace_root  # noqa: E402
from app.deps import get_settings  # noqa: E402
from app.services.workbook.constants import CONFIRM_PHRASE, DEFAULT_WORKBOOK  # noqa: E402
from app.services.workbook.migrate import WorkbookMigrationError, run_workbook_migration  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Migração workbook GET v1 (dry-run por defeito).")
    parser.add_argument("--workbook", type=Path, default=Path(DEFAULT_WORKBOOK))
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Aplicar após validação do report.json (senão dry-run)")
    parser.add_argument("--confirm", default=None, help=f"Frase obrigatória com --apply: {CONFIRM_PHRASE}")
    args = parser.parse_args()

    dry_run = not args.apply
    if args.apply and args.confirm != CONFIRM_PHRASE:
        print(f"--apply exige --confirm {CONFIRM_PHRASE}", file=sys.stderr)
        return 2

    settings: AppSettings = get_settings()
    workspace_root = args.workspace_root.resolve()
    if not workspace_root.is_dir():
        print(f"Workspace inválido: {workspace_root}", file=sys.stderr)
        return 2

    set_active_workspace_root(settings, workspace_root)
    if get_active_workspace_root(settings) != workspace_root:
        print("Falha ao activar workspace.", file=sys.stderr)
        return 2

    try:
        result = run_workbook_migration(
            settings,
            args.workbook,
            dry_run=dry_run,
            confirm=args.confirm,
        )
    except WorkbookMigrationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"run_id={result.run_id}")
    print(f"report={result.report_path}")
    print(f"blocking_errors={result.blocking_errors} warnings={result.warnings}")
    if result.applied:
        print(f"project_id={result.project_id}")
    if result.blocking_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())