"""Tipos partilhados para catálogos de estrutura documental."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.structure_seed.ctbj_parser import ComplementRule


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
    purpose: str = ""
    blocks: list[BlockSpec] = field(default_factory=list)


@dataclass
class StructureCatalog:
    id: str
    version: int
    checksum: str
    fascicles: list[FascicleSpec]
    complements: list[ComplementRule] = field(default_factory=list)
    display_name: str = ""

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


# Alias histórico
CtbjCatalog = StructureCatalog