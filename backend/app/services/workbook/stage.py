from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.workbook.constants import WORKBOOK_IMPORT_VERSION
from app.services.workbook.mapping import mapping_document
from app.services.workbook.types import WorkbookBundle, MigrationIssue


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bundle_preview(bundle: WorkbookBundle) -> dict[str, Any]:
    return {
        "project_name": bundle.project_name,
        "counts": {
            "fascicles": len(bundle.fascicles),
            "blocks": len(bundle.blocks),
            "principles": len(bundle.principles),
            "artefacts": len(bundle.artefacts),
            "a01_rows": len(bundle.a01_rows),
            "references": len(bundle.references),
        },
        "fascicles_preview": [
            {"codigo": f.codigo, "designacao": f.designacao} for f in bundle.fascicles[:5]
        ],
        "blocks_preview": [
            {"block_code": b.block_code, "fasciculo": b.fasciculo, "title": b.block_title}
            for b in bundle.blocks[:5]
        ],
    }


def _staging_payloads(bundle: WorkbookBundle) -> dict[str, list[dict[str, Any]]]:
    return {
        "fascicles": [f.__dict__ for f in bundle.fascicles],
        "blocks": [b.__dict__ for b in bundle.blocks],
        "principles": [p.__dict__ for p in bundle.principles],
        "artefacts": [a.__dict__ for a in bundle.artefacts],
        "a01_rows": [r.__dict__ for r in bundle.a01_rows],
        "references": [r.__dict__ for r in bundle.references],
    }


def write_migration_report(
    reports_root: Path,
    bundle: WorkbookBundle,
    issues: list[MigrationIssue],
    *,
    run_id: str | None = None,
    mode: str = "dry-run",
) -> Path:
    run_id = run_id or str(uuid.uuid4())
    run_dir = reports_root / run_id
    staging_dir = run_dir / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    blocking = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")

    report: dict[str, Any] = {
        "schema": "workbook-migration-report-v1",
        "workbook_import_version": WORKBOOK_IMPORT_VERSION,
        "run_id": run_id,
        "generated_at": _utcnow(),
        "mode": mode,
        "workbook_path": bundle.workbook_path,
        "workbook_sha256": bundle.workbook_sha256,
        "project_context": bundle.project_context,
        "preview": _bundle_preview(bundle),
        "mapping": mapping_document(),
        "counts": _bundle_preview(bundle)["counts"],
        "blocking_errors": blocking,
        "warnings": warnings,
        "issues": [i.as_dict() for i in issues],
        "status": "blocked" if blocking else "ready",
    }

    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    for entity, rows in _staging_payloads(bundle).items():
        (staging_dir / f"{entity}.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return report_path