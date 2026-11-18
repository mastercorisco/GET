#!/usr/bin/env python3
"""Remove a árvore documental de um projecto (mantém o projecto, referências, biblioteca)."""

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
from app.services.deletion_service import purge_project_document_structure  # noqa: E402
from app.services.project_service import list_projects  # noqa: E402


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
            if "belo jardim" in p.name.lower() or "ctbj" in p.name.lower()
        ]
    if not matches:
        raise SystemExit("Nenhum projecto encontrado.")
    if len(matches) > 1:
        raise SystemExit(
            "Vários projectos: " + ", ".join(f"{p.name} ({p.id})" for p in matches)
        )
    return matches[0].id


def main() -> int:
    parser = argparse.ArgumentParser(description="Purgar estrutura documental de um projecto.")
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--project-id", default=None)
    parser.add_argument("--project-name", default=None)
    parser.add_argument("--apply", action="store_true", help="Executar (cria backup crítico)")
    args = parser.parse_args()

    if not args.apply:
        print("Dry-run: use --apply para purgar (com backup crítico).", file=sys.stderr)
        return 2

    root = args.workspace_root.resolve()
    settings: AppSettings = get_settings()
    set_active_workspace_root(settings, root)
    if get_active_workspace_root(settings) != root:
        print("Falha ao activar workspace.", file=sys.stderr)
        return 2

    project_id = _resolve_project_id(settings, args.project_id, args.project_name)
    backup = create_backup(settings, "critical")
    print(f"backup_id={backup.id}")
    print(f"project_id={project_id}")
    stats = purge_project_document_structure(settings, project_id)
    print(stats)
    if stats["document_nodes_remaining"] or stats["development_points_remaining"]:
        print("AVISO: ainda restam nós ou pontos.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())