"""Remove projectos de teste (nome exacto 'Export project') do workspace configurado."""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from app.deps import get_settings
from app.models.project import Project
from app.services.deletion_service import delete_project
from app.services.workspace_service import workspace_session

EXPORT_NAME = "Export project"


def main() -> int:
    keep_name_substr = os.environ.get("GET_PURGE_KEEP_NAME_SUBSTR", "").strip()
    dry_run = os.environ.get("GET_PURGE_DRY_RUN", "") in ("1", "true", "yes")
    settings = get_settings()
    with workspace_session(settings) as (session, _paths):
        rows = [(p.id, p.name) for p in session.scalars(select(Project).order_by(Project.created_at))]
    to_delete = [pid for pid, name in rows if name == EXPORT_NAME]
    keep = [(pid, name) for pid, name in rows if name != EXPORT_NAME]
    if keep_name_substr:
        keep = [(pid, name) for pid, name in keep if keep_name_substr.lower() in name.lower()]
    print(f"workspace: {settings.workspace_root}")
    print(f"manter ({len(keep)}):")
    for pid, name in keep:
        print(f"  {pid[:8]}… {name}")
    print(f"apagar ({len(to_delete)}): nome == {EXPORT_NAME!r}")
    if dry_run:
        return 0
    failed: list[tuple[str, str]] = []
    for i, pid in enumerate(to_delete, 1):
        try:
            delete_project(settings, pid)
            print(f"  [{i}/{len(to_delete)}] ok {pid[:8]}")
        except Exception as exc:
            failed.append((pid, str(exc)))
            print(f"  [{i}/{len(to_delete)}] FAIL {pid[:8]}: {exc}")
    with workspace_session(settings) as (session, _paths):
        remaining = [(p.id, p.name) for p in session.scalars(select(Project))]
    print(f"restantes: {len(remaining)}")
    for pid, name in remaining:
        print(f"  {pid[:8]}… {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())