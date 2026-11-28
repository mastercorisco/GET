"""Carregar o catálogo CTBJ v3 compilado."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.structure_seed.catalog_loader import structure_catalog_from_json
from app.services.structure_seed.catalog_types import (
    BlockSpec,
    CtbjCatalog,
    FascicleSpec,
    StructureCatalog,
)
from app.services.structure_seed.ctbj_parser import (
    ComplementRule,
    apply_complements_to_catalog,
    parse_ctbj_v3_inventory,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CATALOG = REPO_ROOT / "catalogs" / "ctbj_document_structure_v3.pt-PT.json"
DEFAULT_INVENTORY = REPO_ROOT / "docs" / "inventory" / "ctbj_structure_v3.inventory.md"


def _from_json(data: dict) -> StructureCatalog:
    return structure_catalog_from_json(data)


def _apply_json_complements(catalog: StructureCatalog) -> None:
    from app.services.structure_seed.ctbj_parser import CatalogBlock, CatalogFascicle, CatalogPoint, ParsedCatalog

    parsed = ParsedCatalog(fascicles=[], complements=catalog.complements)
    for f in catalog.fascicles:
        blocks = [
            CatalogBlock(
                code=b.code,
                fascicle_code=f.code,
                ordinal=b.ordinal,
                title=b.title,
                development_points=[CatalogPoint(text=t) for t in b.development_points],
            )
            for b in f.blocks
        ]
        parsed.fascicles.append(
            CatalogFascicle(code=f.code, ordinal=f.ordinal, title=f.title, blocks=blocks)
        )
    apply_complements_to_catalog(parsed)
    for f_cat, f_parsed in zip(catalog.fascicles, parsed.fascicles):
        for b_cat, b_parsed in zip(f_cat.blocks, f_parsed.blocks):
            b_cat.development_points = [p.text for p in b_parsed.development_points]


def load_ctbj_catalog(
    path: Path | None = None,
    *,
    apply_complements: bool = True,
) -> StructureCatalog:
    catalog_path = path or DEFAULT_CATALOG
    if catalog_path.is_file():
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog = _from_json(data)
    elif DEFAULT_INVENTORY.is_file():
        text = DEFAULT_INVENTORY.read_text(encoding="utf-8")
        parsed = parse_ctbj_v3_inventory(text, apply_complements=False)
        catalog = StructureCatalog(
            id="ctbj_v3",
            version=3,
            checksum="",
            fascicles=[
                FascicleSpec(
                    code=f.code,
                    ordinal=f.ordinal,
                    title=f.title,
                    blocks=[
                        BlockSpec(
                            code=b.code,
                            fascicle_code=f.code,
                            ordinal=b.ordinal,
                            title=b.title,
                            development_points=[p.text for p in b.development_points],
                        )
                        for b in f.blocks
                    ],
                )
                for f in parsed.fascicles
            ],
            complements=parsed.complements,
            display_name="CTBJ v3",
        )
    else:
        raise FileNotFoundError(f"Catálogo CTBJ em falta: {catalog_path}")

    if apply_complements and catalog.complements:
        _apply_json_complements(catalog)
    return catalog