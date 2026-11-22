#!/usr/bin/env python3
"""F2 / M2 — pré-voo GET-LLM (bloco com pontos exportáveis)."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sqlalchemy import func, select

from app.deps import get_settings
from app.domain.block.models import DevelopmentPoint
from app.models.baseline import BaselineDocumentCode
from app.models.document import DocumentNode
from app.schemas.export import LlmGenerationExportRequest
from app.services.export_service import ExportError, export_llm_generation
from app.services.llm_export.block_eligibility import export_status_for_point
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def _resolve_block(session, project_id: str, code: str) -> tuple[str, str | None]:
    code_norm = code.strip().upper()
    row = session.execute(
        select(BaselineDocumentCode.document_node_id, DocumentNode.parent_id)
        .join(DocumentNode, DocumentNode.id == BaselineDocumentCode.document_node_id)
        .where(
            DocumentNode.project_id == project_id,
            DocumentNode.node_type == "block",
            func.upper(BaselineDocumentCode.display_code) == code_norm,
        )
        .limit(1)
    ).first()
    if not row:
        raise ProjectError(f"Bloco {code_norm!r} não encontrado.")
    block_id, parent_id = row
    return block_id, parent_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Pré-voo piloto M2 (GET-LLM).")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07")
    parser.add_argument("--profile", default="discussion")
    parser.add_argument("--include-draft", action="store_true")
    parser.add_argument("--export", action="store_true", help="Gerar pacote GET-LLM (fascículo do bloco)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    block_id = ""
    fascicle_id: str | None = None
    counts: dict[str, int] = {}
    exportable = 0

    with workspace_session(settings) as (session, _paths):
        try:
            block_id, fascicle_id = _resolve_block(session, args.project_id, args.block)
        except ProjectError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1

        rows = session.execute(
            select(DevelopmentPoint.status, func.count())
            .where(DevelopmentPoint.block_id == block_id)
            .group_by(DevelopmentPoint.status)
        ).all()
        counts = {str(s): int(c) for s, c in rows}
        points = session.scalars(select(DevelopmentPoint).where(DevelopmentPoint.block_id == block_id)).all()
        exportable = sum(
            1 for p in points if export_status_for_point(p, include_draft=args.include_draft) is not None
        )

    export_payload = None
    if args.export:
        if not fascicle_id:
            print("ERRO: bloco sem fascículo pai.", file=sys.stderr)
            return 1
        if exportable == 0:
            print("ERRO: nenhum ponto exportável — marque ready/approved ou use --include-draft.", file=sys.stderr)
            return 1
        try:
            result = export_llm_generation(
                settings,
                args.project_id,
                LlmGenerationExportRequest(
                    profile=args.profile,
                    include_draft=args.include_draft,
                    fascicle_node_id=fascicle_id,
                ),
            )
        except ExportError as exc:
            print(f"ERRO export: {exc}", file=sys.stderr)
            return 1
        term_in_zip = False
        with zipfile.ZipFile(result.zip_path, "r") as zf:
            names = zf.namelist()
            term_in_zip = any(n.startswith("terminology_") and n.endswith("_llm.md") for n in names)
        export_payload = {
            "export_id": result.export_id,
            "zip_path": result.zip_path,
            "master_path": result.file_path,
            "terminology_in_zip": term_in_zip,
        }

    payload = {
        "project_id": args.project_id,
        "block": args.block.upper(),
        "block_id": block_id,
        "fascicle_id": fascicle_id,
        "point_status_counts": counts,
        "exportable_points": exportable,
        "export": export_payload,
    }

    if args.json:
        print(json.dumps(payload, default=str, indent=2))
    else:
        print(f"Bloco {args.block.upper()}: status={counts}")
        print(f"Pontos exportáveis GET-LLM: {exportable} (include_draft={args.include_draft})")
        if export_payload:
            print(f"Export: {export_payload['export_id']} → {export_payload['zip_path']}")
            print(f"Glossário no ZIP: {export_payload['terminology_in_zip']}")
        else:
            print("Dica: --export após ≥1 ponto ready; depois sessão get-write-spec.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())