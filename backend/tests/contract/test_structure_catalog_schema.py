from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "catalog_file",
    [
        "structure_catalog_generic_example.pt-PT.json",
        "ctbj_document_structure_v3.pt-PT.json",
    ],
)
def test_structure_catalog_files_validate(catalog_file: str) -> None:
    schema = json.loads((REPO_ROOT / "schemas" / "structure_catalog.schema.json").read_text(encoding="utf-8"))
    path = REPO_ROOT / "catalogs" / catalog_file
    instance = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=instance, schema=schema)