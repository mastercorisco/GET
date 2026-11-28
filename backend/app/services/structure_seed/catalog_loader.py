"""Carregar StructureCatalog a partir de JSON no repositório."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.structure_seed.catalog_types import BlockSpec, FascicleSpec, StructureCatalog
from app.services.structure_seed.ctbj_parser import ComplementRule


def structure_catalog_from_json(data: dict) -> StructureCatalog:
    fascicles: list[FascicleSpec] = []
    for f in data["fascicles"]:
        blocks = []
        for b in f["blocks"]:
            pts_raw = b.get("development_points") or []
            pts = [p["text"] if isinstance(p, dict) else str(p) for p in pts_raw]
            blocks.append(
                BlockSpec(
                    code=b["code"],
                    fascicle_code=f["code"],
                    ordinal=int(b["ordinal"]),
                    title=b["title"],
                    development_points=pts,
                )
            )
        fascicles.append(
            FascicleSpec(
                code=f["code"],
                ordinal=int(f["ordinal"]),
                title=f["title"],
                purpose=str(f.get("purpose") or ""),
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
    return StructureCatalog(
        id=data.get("id", ""),
        version=int(data.get("version", 1)),
        checksum=data.get("checksum", ""),
        fascicles=fascicles,
        complements=complements,
        display_name=str(data.get("display_name") or ""),
    )


def load_structure_catalog_file(path: Path) -> StructureCatalog:
    if not path.is_file():
        raise FileNotFoundError(f"Catálogo em falta: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return structure_catalog_from_json(data)