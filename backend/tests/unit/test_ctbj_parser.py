from __future__ import annotations

from pathlib import Path

from app.services.structure_seed.ctbj_parser import parse_ctbj_v3_inventory

REPO = Path(__file__).resolve().parents[3]
INVENTORY = REPO / "docs" / "inventory" / "ctbj_structure_v3.inventory.md"


def test_ctbj_inventory_totals() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    parsed = parse_ctbj_v3_inventory(text)
    assert parsed.fascicle_count == 20
    assert parsed.block_count == 179
    assert parsed.point_count == 869
    assert len(parsed.complements) >= 8


def test_ctbj_complements_apply_replace_generic() -> None:
    text = INVENTORY.read_text(encoding="utf-8")
    parsed = parse_ctbj_v3_inventory(text, apply_complements=True)
    f11 = next(f for f in parsed.fascicles if f.code == "F11")
    first = f11.blocks[0]
    assert not first.development_points[0].text.startswith("Definir o âmbito")