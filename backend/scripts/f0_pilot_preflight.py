#!/usr/bin/env python3
"""Pré-voo F0 — resumo M0, fascículo por código e export GET-PACKAGE opcional."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sqlalchemy import func, select

from app.deps import get_settings
from app.domain.block.models import DevelopmentPoint
from app.models.baseline import BaselineDocumentCode
from app.models.document import DocumentNode
from app.schemas.packages import PackageExportRequest
from app.services.package_service import PackageError, export_package
from app.services.project_service import ProjectError
from app.services.project_summary_service import get_project_summary
from app.services.workspace_service import workspace_session


def _resolve_fascicle_id(session, project_id: str, code: str) -> tuple[str, str]:
    rows = session.scalars(
        select(DocumentNode).where(
            DocumentNode.project_id == project_id,
            DocumentNode.node_type == "fascicle",
        )
    ).all()
    for node in rows:
        display = session.scalar(
            select(BaselineDocumentCode.display_code).where(
                BaselineDocumentCode.document_node_id == node.id
            ).limit(1)
        )
        if (display or "").upper() == code.upper():
            return node.id, node.title
    raise ProjectError(f"Fascículo «{code}» não encontrado no projecto.")


def _fascicle_blocks(session, fascicle_id: str) -> list[dict]:
    blocks = session.scalars(
        select(DocumentNode)
        .where(DocumentNode.parent_id == fascicle_id, DocumentNode.node_type == "block")
        .order_by(DocumentNode.sort_key)
    ).all()
    out: list[dict] = []
    for block in blocks:
        display = session.scalar(
            select(BaselineDocumentCode.display_code).where(
                BaselineDocumentCode.document_node_id == block.id
            ).limit(1)
        )
        pt_count = session.scalar(
            select(func.count()).select_from(DevelopmentPoint).where(DevelopmentPoint.block_id == block.id)
        )
        out.append(
            {
                "display_code": display or "",
                "block_id": block.id,
                "title": block.title,
                "point_count": int(pt_count or 0),
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Pré-voo piloto F0-structure (M0).")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--fascicle", default="F01", help="Código documental do fascículo (ex. F01)")
    parser.add_argument("--export", action="store_true", help="Gerar GET-PACKAGE fascículo (PKG-FASC-*)")
    parser.add_argument("--json", action="store_true", help="Saída JSON (senão texto)")
    args = parser.parse_args()

    settings = get_settings()
    try:
        summary = get_project_summary(settings, args.project_id)
    except ProjectError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    with workspace_session(settings) as (session, paths):
        try:
            fascicle_id, fascicle_title = _resolve_fascicle_id(session, args.project_id, args.fascicle)
        except ProjectError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1
        blocks = _fascicle_blocks(session, fascicle_id)
        backups = sorted(
            (paths.root / "backups" / "critical").glob("*.db"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        backup_names = [b.name for b in backups[:5]]

    export_result = None
    if args.export:
        try:
            export_result = export_package(
                settings,
                args.project_id,
                PackageExportRequest(
                    scope_kind="fascicle",
                    node_id=fascicle_id,
                    profile="discussion",
                    llm_notes="F0-structure piloto (preflight script)",
                ),
            )
        except PackageError as exc:
            print(f"ERRO export: {exc}", file=sys.stderr)
            return 1

    payload = {
        "project_id": args.project_id,
        "summary": summary.model_dump(),
        "fascicle": {
            "code": args.fascicle.upper(),
            "node_id": fascicle_id,
            "title": fascicle_title,
            "blocks": blocks,
        },
        "backups_critical_recent": backup_names,
        "export": None,
    }
    if export_result is not None:
        payload["export"] = {
            "export_id": export_result.export_id,
            "file_path": export_result.file_path,
            "filename": export_result.filename,
            "sha256": export_result.sha256,
        }

    if args.json:
        print(json.dumps(payload, default=str, indent=2))
    else:
        print(f"Projecto: {args.project_id}")
        print(f"Pontos por status: {summary.point_status_counts}")
        print(f"Staging: imports_staged={summary.imports_staged}, merges_open={summary.merge_sessions_open}")
        print(f"Fascículo {args.fascicle}: {fascicle_id} — {fascicle_title}")
        print(f"Blocos ({len(blocks)}):")
        for row in blocks:
            print(f"  {row['display_code']}: {row['point_count']} pts — {row['title'][:60]}")
        if backup_names:
            print(f"Backups recentes: {', '.join(backup_names[:3])}")
        if export_result:
            print(f"Export: {export_result.export_id} → {export_result.file_path}")
        else:
            print("Dica: acrescente --export para gerar PKG-FASC-* antes da sessão LLM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())