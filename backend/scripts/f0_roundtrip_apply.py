#!/usr/bin/env python3
"""GET-PACKAGE: import → merge → aceitar propostas → consolidate (CLI; F0/F1)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from app.deps import get_settings
from app.schemas.imports import ProposalDecisionRequest
from app.services.imports.consolidate import ConsolidateError
from app.services.package_service import (
    PackageError,
    consolidate_package,
    import_package,
    merge_response,
    run_package_merge,
)
from app.services.import_service import ImportError, decide_proposal

_STRUCTURE_KINDS = frozenset({"structure"})
_F0_SAFE_KINDS = frozenset(
    {"structure", "block_field", "point_update", "point_create", "premise_update", "premise_create"}
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aplicar import GET-PACKAGE (fascículo F0 / bloco F1).")
    parser.add_argument("path", type=Path, help="JSON devolvido (dry-run ou LLM)")
    parser.add_argument("--project-id", required=True)
    parser.add_argument(
        "--accept",
        choices=("auto", "structure-only", "f0-safe", "all-pending"),
        default="auto",
        help="auto=fascicle→structure-only, block→f0-safe",
    )
    parser.add_argument("--dry-run", action="store_true", help="Só import + merge; não decide nem consolida")
    args = parser.parse_args()

    path = args.path.resolve()
    if not path.is_file():
        print(f"ERRO: ficheiro em falta: {path}", file=sys.stderr)
        return 2

    raw = path.read_bytes()
    settings = get_settings()

    try:
        imported = import_package(settings, args.project_id, path.name, raw)
    except PackageError as exc:
        print(f"ERRO import: {exc}", file=sys.stderr)
        return 1

    print(f"Import: {imported.import_id} · scope={imported.scope_kind} · warnings={len(imported.conceptual_warnings)}")
    for w in imported.conceptual_warnings:
        print(f"  AVISO: {w}")

    try:
        merge_id = run_package_merge(settings, args.project_id, imported.import_id)
        merge = merge_response(settings, merge_id)
    except PackageError as exc:
        print(f"ERRO merge: {exc}", file=sys.stderr)
        return 1

    proposals = merge.proposals
    print(f"Merge: {merge_id} · propostas={len(proposals)}")
    for prop in proposals:
        print(f"  - {prop.proposal_kind}: {prop.title[:80]}")

    if args.dry_run:
        print("Dry-run: parado antes de decisões.")
        return 0

    accept_mode = args.accept
    if accept_mode == "auto":
        accept_mode = "structure-only" if imported.scope_kind == "fascicle" else "f0-safe"
        print(f"Aceitação auto: {accept_mode} (scope={imported.scope_kind})")

    if accept_mode == "structure-only":
        allowed = _STRUCTURE_KINDS
    elif accept_mode == "f0-safe":
        allowed = _F0_SAFE_KINDS
    else:
        allowed = None

    accepted = 0
    skipped = 0
    for prop in proposals:
        if allowed is not None and prop.proposal_kind not in allowed:
            print(f"SKIP (não aceite auto): {prop.proposal_kind} · {prop.title[:60]}")
            skipped += 1
            continue
        try:
            decide_proposal(
                settings,
                merge_id,
                prop.id,
                ProposalDecisionRequest(
                    decision="accepted",
                    destination="project",
                    confirmed_protected=prop.protected_touch,
                ),
            )
            accepted += 1
        except ImportError as exc:
            print(f"ERRO decisão {prop.id}: {exc}", file=sys.stderr)
            return 1

    if accepted == 0 and proposals:
        print("ERRO: nenhuma proposta aceite; não consolidando.", file=sys.stderr)
        return 1
    if not proposals:
        print("Sem propostas — nada a consolidar.")
        return 0

    try:
        backup_id = consolidate_package(settings, merge_id)
    except ConsolidateError as exc:
        print(f"ERRO consolidate: {exc}", file=sys.stderr)
        return 1

    print(f"Consolidado. backup_id={backup_id} · aceites={accepted} · omitidas={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())