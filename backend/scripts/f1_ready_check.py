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
from app.domain.block.schemas import DevelopmentPointPatch
from app.domain.block.service import patch_point, suggested_status, validate_point
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


_MARKABLE_STATUSES = frozenset({"draft", "incomplete"})


def _harness_reports(session, block_id: str) -> list[dict]:
    points = session.scalars(
        select(DevelopmentPoint)
        .where(DevelopmentPoint.block_id == block_id)
        .order_by(DevelopmentPoint.sort_order)
    ).all()
    siblings = list(points)
    lines: list[dict] = []
    for point in points:
        issues = validate_point(session, point, sibling_points=siblings)
        suggested = suggested_status(point, issues)
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        grill_ready = suggested == "ready" and not errors
        markable = grill_ready and point.status in _MARKABLE_STATUSES
        lines.append(
            {
                "point_id": point.id,
                "title": point.title,
                "status": point.status,
                "suggested_status": suggested,
                "grill_ready": grill_ready,
                "markable_ready": markable,
                "needs_review": point.needs_review,
                "error_count": len(errors),
                "warning_count": len(warnings),
                "errors": [{"code": i.code, "message": i.message} for i in errors],
            }
        )
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Checklist harness F1 (pré-marcar ready na UI).")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07", help="display_code do bloco")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--apply-ready",
        action="store_true",
        help="Marcar ready nos candidatos com harness válido (draft/incomplete).",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Obrigatório com --apply-ready (confirmação explícita do engenheiro).",
    )
    args = parser.parse_args()

    if args.apply_ready and not args.confirm:
        print("ERRO: use --confirm com --apply-ready.", file=sys.stderr)
        return 2

    settings = get_settings()
    lines: list[dict] = []
    applied = 0
    with workspace_session(settings) as (session, _paths):
        try:
            block_id = _resolve_block(session, args.project_id, args.block)
        except ProjectError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1

        lines = _harness_reports(session, block_id)
        mark_ids = [r["point_id"] for r in lines if r["markable_ready"]] if args.apply_ready else []

    for pid in mark_ids:
        patch_point(settings, pid, DevelopmentPointPatch(status="ready"))
        applied += 1

    if applied:
        with workspace_session(settings) as (session, _paths):
            block_id = _resolve_block(session, args.project_id, args.block)
            lines = _harness_reports(session, block_id)

    ready_candidates = sum(1 for r in lines if r["grill_ready"] and r["status"] not in ("ready", "approved"))

    payload = {
        "project_id": args.project_id,
        "block": args.block.upper(),
        "point_count": len(lines),
        "ready_candidates": ready_candidates,
        "applied_ready": applied,
        "points": lines,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if applied:
            print(f"Aplicado: {applied} ponto(s) → ready.")
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