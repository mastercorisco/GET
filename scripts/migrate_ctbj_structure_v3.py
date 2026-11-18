#!/usr/bin/env python3
"""Migração / seed da estrutura documental CTBJ v3 num workspace."""

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
from app.services.backup_service import create_backup  # noqa: E402
from app.services.project_service import list_projects  # noqa: E402
from app.services.structure_seed.ctbj_v3_sync import apply_ctbj_v3_structure  # noqa: E402
from app.services.workspace_service import workspace_session  # noqa: E402
from app.domain.block.block_enrichment import enrich_project_authoring  # noqa: E402
from app.domain.block.ordering import normalize_project_block_point_orders  # noqa: E402


def _resolve_project_id(settings: AppSettings, project_id: str | None, project_name: str | None) -> str:
    if project_id:
        return project_id
    projects = list_projects(settings)
    if project_name:
        matches = [p for p in projects if project_name.lower() in p.name.lower()]
    else:
        matches = [
            p
            for p in projects
            if "ctbj" in p.name.lower() or "belo jardim" in p.name.lower()
        ]
    if not matches:
        raise SystemExit("Nenhum projecto encontrado. Use --project-id ou --project-name.")
    if len(matches) > 1:
        raise SystemExit(
            "Vários projectos correspondem: "
            + ", ".join(f"{p.name} ({p.id})" for p in matches)
        )
    return matches[0].id


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincronizar estrutura CTBJ v3 (dry-run por defeito).")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--project-name", default=None)
    parser.add_argument("--apply", action="store_true", help="Aplicar alterações (cria backup crítico)")
    parser.add_argument("--seed-empty", action="store_true", help="Modo seed sem heurística de match")
    parser.add_argument(
        "--renumber-points",
        action="store_true",
        help="Só renumera pontos 1..n em cada bloco (sem sincronizar árvore)",
    )
    parser.add_argument(
        "--authoring-ready",
        action="store_true",
        help="Preenche objectivo/âmbito dos blocos e classifica pontos ready+strict",
    )
    args = parser.parse_args()

    dry_run = not args.apply
    workspace_root = args.workspace_root.resolve()
    if not workspace_root.is_dir():
        print(f"Workspace inválido: {workspace_root}", file=sys.stderr)
        return 2

    settings: AppSettings = get_settings()
    set_active_workspace_root(settings, workspace_root)
    if get_active_workspace_root(settings) != workspace_root:
        print("Falha ao activar workspace.", file=sys.stderr)
        return 2

    try:
        project_id = _resolve_project_id(settings, args.project_id, args.project_name)
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.authoring_ready:
        if dry_run:
            print("--authoring-ready exige --apply.", file=sys.stderr)
            return 2
        backup_id = create_backup(settings, "critical").id
        print(f"backup_id={backup_id}")
        with workspace_session(settings) as (session, _paths):
            stats = enrich_project_authoring(session, project_id, run_id="authoring_cli")
        print(f"authoring headers_patched={stats['headers_patched']} ready={stats['points_ready']} strict={stats['strict_points']} draft_left={stats['draft_remaining']}")
        return 0

    if args.renumber_points:
        if dry_run:
            print("--renumber-points exige --apply (altera sort_order na base).", file=sys.stderr)
            return 2
        backup_id = create_backup(settings, "critical").id
        print(f"backup_id={backup_id}")
        with workspace_session(settings) as (session, _paths):
            stats = normalize_project_block_point_orders(session, project_id, run_id="renumber_cli")
        print(f"renumber blocks_touched={stats['blocks_touched']} points={stats['points_renumbered']}")
        return 0

    backup_id = None
    if not dry_run:
        backup_id = create_backup(settings, "critical").id
        print(f"backup_id={backup_id}")

    mode = "seed_empty" if args.seed_empty else "migrate"
    result = apply_ctbj_v3_structure(
        settings,
        project_id,
        mode=mode,
        dry_run=dry_run,
        backup_id=backup_id,
    )

    print(f"run_id={result.run_id}")
    print(f"project_id={result.project_id}")
    print(f"report={result.report_path}")
    print(
        f"catalog={result.fascicles}/{result.blocks}/{result.catalog_points} "
        f"applied={result.applied} skipped={result.skipped}"
    )
    for warn in result.warnings[:20]:
        print(f"warning: {warn}")
    if len(result.warnings) > 20:
        print(f"... mais {len(result.warnings) - 20} avisos")
    for err in result.blocking_errors:
        print(f"ERROR: {err}", file=sys.stderr)

    if result.blocking_errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())