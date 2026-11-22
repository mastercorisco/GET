#!/usr/bin/env python3
"""F1 — pré-voo bloco: contagens por status + export GET-PACKAGE opcional."""

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


def _resolve_block(session, project_id: str, code: str) -> tuple[str, str]:
    block_id = session.scalar(
        select(BaselineDocumentCode.document_node_id)
        .join(DocumentNode, DocumentNode.id == BaselineDocumentCode.document_node_id)
        .where(
            DocumentNode.project_id == project_id,
            DocumentNode.node_type == "block",
            BaselineDocumentCode.display_code == code,
        )
        .limit(1)
    )
    if not block_id:
        raise ProjectError(f"Bloco {code!r} não encontrado.")
    block = session.get(DocumentNode, block_id)
    title = block.title if block else ""
    return block_id, title


def main() -> int:
    parser = argparse.ArgumentParser(description="Pré-voo piloto F1 (get-grill).")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07", help="display_code do bloco")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    try:
        summary = get_project_summary(settings, args.project_id)
    except ProjectError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    with workspace_session(settings) as (session, _paths):
        try:
            block_id, block_title = _resolve_block(session, args.project_id, args.block.upper())
        except ProjectError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1

        status_rows = session.execute(
            select(DevelopmentPoint.status, func.count())
            .where(DevelopmentPoint.block_id == block_id)
            .group_by(DevelopmentPoint.status)
        ).all()
        by_status = {str(s): int(c) for s, c in status_rows}

        points = session.scalars(
            select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id).order_by(DevelopmentPoint.sort_order)
        ).all()
        point_list = [
            {"id": p.id, "status": p.status, "title": p.title, "needs_review": p.needs_review}
            for p in points
        ]

    export_result = None
    if args.export:
        try:
            export_result = export_package(
                settings,
                args.project_id,
                PackageExportRequest(
                    scope_kind="block",
                    node_id=block_id,
                    profile="discussion",
                    llm_notes="F1 grill piloto",
                ),
            )
        except PackageError as exc:
            print(f"ERRO export: {exc}", file=sys.stderr)
            return 1

    payload = {
        "project_id": args.project_id,
        "summary_project": summary.model_dump(),
        "block": {
            "display_code": args.block.upper(),
            "node_id": block_id,
            "title": block_title,
            "point_status_counts": by_status,
            "points": point_list,
        },
        "export": None,
    }
    if export_result:
        payload["export"] = {
            "export_id": export_result.export_id,
            "file_path": export_result.file_path,
            "filename": export_result.filename,
        }

    if args.json:
        print(json.dumps(payload, default=str, indent=2))
    else:
        print(f"Projecto {args.project_id}: {summary.point_status_counts}")
        print(f"Bloco {args.block}: {block_id} — {block_title}")
        print(f"Status no bloco: {by_status}")
        for p in point_list:
            rev = " · rev" if p["needs_review"] else ""
            print(f"  [{p['status']}{rev}] {p['title'][:65]}")
        if export_result:
            print(f"Export: {export_result.export_id} → {export_result.file_path}")
        else:
            print("Dica: use --export antes da sessão get-grill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())