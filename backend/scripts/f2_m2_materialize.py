#!/usr/bin/env python3
"""F2 — materializar ficheiros GET-LLM de um bloco para redação (fora do GET)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sqlalchemy import func, select

from app.deps import get_settings
from app.models.baseline import BaselineDocumentCode
from app.models.document import DocumentNode
from app.services.project_service import ProjectError
from app.services.workspace_service import workspace_session


def _resolve_block_code(session, project_id: str, code: str) -> str:
    code_norm = code.strip().upper()
    found = session.scalar(
        select(BaselineDocumentCode.display_code)
        .join(DocumentNode, DocumentNode.id == BaselineDocumentCode.document_node_id)
        .where(
            DocumentNode.project_id == project_id,
            DocumentNode.node_type == "block",
            func.upper(BaselineDocumentCode.display_code) == code_norm,
        )
        .limit(1)
    )
    if not found:
        raise ProjectError(f"Bloco {code_norm!r} não encontrado.")
    return found


def _must_include_rows(point: dict) -> list[str]:
    rows: list[str] = []
    for item in point.get("must_include") or []:
        if isinstance(item, dict) and item.get("text"):
            rows.append(str(item["text"]))
        elif isinstance(item, str):
            rows.append(item)
    lists = point.get("lists") or {}
    for item in lists.get("must_include") or []:
        if isinstance(item, dict) and item.get("text"):
            rows.append(str(item["text"]))
    return rows


def _write_outline(block_json: Path, dest: Path, block_code: str) -> Path:
    data = json.loads(block_json.read_text(encoding="utf-8"))
    block = data.get("block") or {}
    points = (data.get("preparation") or {}).get("development_points") or []
    lines = [
        f"# Esboço de redação — {block_code}",
        "",
        f"**Bloco:** {block.get('title', '')}",
        "",
        "_Substitua cada secção TBD por texto do caderno; não reimportar este ficheiro no GET._",
        "",
    ]
    for pt in points:
        if pt.get("status") not in ("ready", "approved"):
            continue
        title = pt.get("title") or "(sem título)"
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"**Ideia central (registo):** {pt.get('core_idea', '').strip()}")
        lines.append("")
        must = _must_include_rows(pt)
        if must:
            lines.append("**must_include (cobrir no texto):**")
            for row in must:
                lines.append(f"- {row}")
            lines.append("")
        lines.append("<!-- TBD: redigir corpo do ponto -->")
        lines.append("")
    out = dest / f"REDACAO-{block_code}-outline.md"
    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Copiar GET-LLM do bloco para pasta de redação.")
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--block", default="F04_B07")
    parser.add_argument("--profile", default="discussion")
    parser.add_argument(
        "--dest",
        type=Path,
        help="Pasta destino (predef.: {workspace}/redaction/{block})",
    )
    parser.add_argument("--outline", action="store_true", help="Gerar REDACAO-*-outline.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    with workspace_session(settings) as (session, paths):
        try:
            block_code = _resolve_block_code(session, args.project_id, args.block)
        except ProjectError as exc:
            print(f"ERRO: {exc}", file=sys.stderr)
            return 1
        exp_dir = paths.exports_dir / f"EXP-LLM-{args.project_id[:8]}"
        if not exp_dir.is_dir():
            print(f"ERRO: export em falta: {exp_dir}", file=sys.stderr)
            return 1
        block_json = exp_dir / f"{block_code}_{args.profile}_llm.json"
        block_md = exp_dir / f"{block_code}_{args.profile}_llm.md"
        if not block_json.is_file():
            print(f"ERRO: ficheiro em falta: {block_json}", file=sys.stderr)
            return 1
        dest = args.dest or (paths.root / "redaction" / block_code)
        dest.mkdir(parents=True, exist_ok=True)
        copied = []
        for src in (block_json, block_md):
            if src.is_file():
                shutil.copy2(src, dest / src.name)
                copied.append(src.name)
        for name in (
            f"terminology_{args.profile}_llm.md",
            f"terminology_{args.profile}_llm.json",
            "manifest.json",
        ):
            src = exp_dir / name
            if src.is_file():
                shutil.copy2(src, dest / name)
                copied.append(name)
        outline_path = None
        if args.outline:
            outline_path = _write_outline(block_json, dest, block_code)

    payload = {
        "project_id": args.project_id,
        "block": block_code,
        "export_dir": str(exp_dir),
        "dest": str(dest),
        "copied": copied,
        "outline": str(outline_path) if outline_path else None,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Destino: {dest}")
        for name in copied:
            print(f"  copiado: {name}")
        if outline_path:
            print(f"  outline: {outline_path.name}")
        print("Próximo: editar outline ou MD; depois get-review + f2_review_report.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())