"""Carregar o catálogo CTBJ v3 compilado."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.services.structure_seed.ctbj_parser import (
    ComplementRule,
    apply_complements_to_catalog,
    parse_ctbj_v3_inventory,
)
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CATALOG = REPO_ROOT / "catalogs" / "ctbj_document_structure_v3.pt-PT.json"
DEFAULT_INVENTORY = REPO_ROOT / "docs" / "inventory" / "ctbj_structure_v3.inventory.md"


@dataclass
class BlockSpec:
    code: str
    fascicle_code: str
    ordinal: int
    title: str
    development_points: list[str] = field(default_factory=list)


@dataclass
class FascicleSpec:
    code: str
    ordinal: int
    title: str
    blocks: list[BlockSpec] = field(default_factory=list)


@dataclass
class CtbjCatalog:
    id: str
    version: int
    checksum: str
    fascicles: list[FascicleSpec]
    complements: list[ComplementRule] = field(default_factory=list)

    @property
    def fascicle_count(self) -> int:
        return len(self.fascicles)

    @property
    def block_count(self) -> int:
        return sum(len(f.blocks) for f in self.fascicles)

    @property
    def point_count(self) -> int:
        return sum(len(b.development_points) for f in self.fascicles for b in f.blocks)

    def block_by_code(self) -> dict[str, BlockSpec]:
        out: dict[str, BlockSpec] = {}
        for fascicle in self.fascicles:
            for block in fascicle.blocks:
                out[block.code] = block
        return out


def _from_json(data: dict) -> CtbjCatalog:
    fascicles: list[FascicleSpec] = []
    for f in data["fascicles"]:
        blocks = []
        for b in f["blocks"]:
            pts = [p["text"] if isinstance(p, dict) else str(p) for p in b["development_points"]]
            blocks.append(
                BlockSpec(
                    code=b["code"],
                    fascicle_code=f["code"],
                    ordinal=b["ordinal"],
                    title=b["title"],
                    development_points=pts,
                )
            )
        fascicles.append(
            FascicleSpec(
                code=f["code"],
                ordinal=f["ordinal"],
                title=f["title"],
                blocks=blocks,
            )
        )
    complements: list[ComplementRule] = []
    for row in data.get("complements") or []:
        complements.append(
            ComplementRule(
                target_block_codes=list(row.get("target_block_codes") or []),
                target_fascicle_code=row.get("target_fascicle_code"),
                replace=bool(row.get("replace", True)),
                development_points=list(row.get("development_points") or []),
            )
        )
    return CtbjCatalog(
        id=data.get("id", "ctbj_v3"),
        version=int(data.get("version", 3)),
        checksum=data.get("checksum", ""),
        fascicles=fascicles,
        complements=complements,
    )


def _apply_json_complements(catalog: CtbjCatalog) -> None:
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
) -> CtbjCatalog:
    catalog_path = path or DEFAULT_CATALOG
    if catalog_path.is_file():
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog = _from_json(data)
    elif DEFAULT_INVENTORY.is_file():
        text = DEFAULT_INVENTORY.read_text(encoding="utf-8")
        parsed = parse_ctbj_v3_inventory(text, apply_complements=False)
        catalog = CtbjCatalog(
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
        )
    else:
        raise FileNotFoundError(f"Catálogo CTBJ em falta: {catalog_path}")

    if apply_complements and catalog.complements:
        _apply_json_complements(catalog)
    return catalog