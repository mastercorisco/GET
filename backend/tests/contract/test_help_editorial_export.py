from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EDITORIAL = REPO_ROOT / "catalogs" / "get_help_editorial.pt-PT.json"
CATALOG = REPO_ROOT / "catalogs" / "get_help_catalog.pt-PT.json"


def test_help_editorial_export_present_and_valid() -> None:
    assert EDITORIAL.is_file(), "Corra: python backend/scripts/export_help_editorial.py"
    data = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    assert data.get("document_type") == "get_help_editorial"
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert len(data.get("fields") or {}) == len(catalog.get("fields") or {})
    sample = data["fields"]["development_point.core_idea"]["editable"]
    assert sample.get("purpose_in_app")