from __future__ import annotations

import tempfile
from pathlib import Path

from app.services.workbook.extract import extract_workbook


def validate_workbook_bytes(data: bytes) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp.write(data)
        path = Path(tmp.name)
    try:
        bundle, issues = extract_workbook(path)
    finally:
        path.unlink(missing_ok=True)

    blocking = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    return {
        "valid": bundle is not None and not blocking,
        "blocking_errors": len(blocking),
        "warnings": len(warnings),
        "issues": [i.as_dict() for i in issues],
        "counts": None
        if bundle is None
        else {
            "fascicles": len(bundle.fascicles),
            "blocks": len(bundle.blocks),
            "principles": len(bundle.principles),
            "artefacts": len(bundle.artefacts),
            "a01_rows": len(bundle.a01_rows),
            "references": len(bundle.references),
        },
    }