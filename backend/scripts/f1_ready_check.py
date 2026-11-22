#!/usr/bin/env python3
"""F1 — validação de harness por ponto (validate_point + suggested_status)."""

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
from app.domain.block.service import suggested_status, validate_point
from app.models.baseline import BaselineDocumentCode
from app.models.document import DocumentNode
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def _resolve_block(session, project_id: str, code: str) -> str:
    code_norm = code.strip().upper()
    block_id = session.scalar(
        select(BaselineDocumentCode.document_node_id)
        .join(DocumentNode, DocumentNode.id == BaselineDocumentCode.document_node_id)
        .where(
            DocumentNode.project_id == project_id,
            DocumentNode.node_type == "block",
            func.upper(BaselineDocumentCode.display_code) == code_norm,
        )
        .limit(1)
    )
    if not block_id:
        raise ProjectError(f"Bloco {code_norm!r} não encontrado.")
    return block_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Checklist harness F1 (pré-marcar ready na UI).")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07", help="display_code do bloco")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    lines: list[dict] = []
    with workspace_session(settings) as (session, _paths):
        try:
            block_id = _resolve_block(session, args.project_id, args.block)
        except ProjectError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1

        points = session.scalars(
            select(DevelopmentPoint)
            .where(DevelopmentPoint.block_id == block_id)
            .order_by(DevelopmentPoint.sort_order)
        ).all()
        siblings = list(points)

        ready_candidates = 0
        for point in points:
            issues = validate_point(session, point, sibling_points=siblings)
            suggested = suggested_status(point, issues)
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]
            grill_ready = suggested == "ready" and not errors
            if grill_ready and point.status != "ready":
                ready_candidates += 1
            lines.append(
                {
                    "point_id": point.id,
                    "title": point.title,
                    "status": point.status,
                    "suggested_status": suggested,
                    "grill_ready": grill_ready,
                    "needs_review": point.needs_review,
                    "error_count": len(errors),
                    "warning_count": len(warnings),
                    "errors": [{"code": i.code, "message": i.message} for i in errors],
                }
            )

    payload = {
        "project_id": args.project_id,
        "block": args.block.upper(),
        "point_count": len(lines),
        "ready_candidates": ready_candidates,
        "points": lines,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Bloco {args.block.upper()} — {len(lines)} ponto(s); {ready_candidates} candidato(s) a ready (harness).")
        for row in lines:
            flag = "OK" if row["grill_ready"] else "—"
            rev = " · rev" if row["needs_review"] else ""
            print(
                f"  [{row['status']}{rev}] {row['title'][:62]} → sug. {row['suggested_status']} "
                f"({row['error_count']} err) {flag}"
            )
            for err in row["errors"][:3]:
                print(f"      · {err['message']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())