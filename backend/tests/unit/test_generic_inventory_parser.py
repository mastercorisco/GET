from __future__ import annotations

from pathlib import Path

from app.services.structure_seed.generic_inventory_parser import parse_generic_structure_inventory

REPO_ROOT = Path(__file__).resolve().parents[3]
SAMPLE = REPO_ROOT / "docs" / "inventory" / "structure_catalog_generic_example.inventory.md"


def test_parse_generic_example_inventory() -> None:
    text = SAMPLE.read_text(encoding="utf-8")
    parsed = parse_generic_structure_inventory(text)
    assert parsed.fascicle_count == 1
    assert parsed.block_count == 2
    assert parsed.point_count == 4
    assert parsed.fascicles[0].code == "F00"