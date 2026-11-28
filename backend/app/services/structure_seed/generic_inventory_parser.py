"""Parser genérico de inventário Markdown (Fascículo / Bloco)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_FASCICLE = re.compile(
    r"^#\s+Fasc[ií]culo\s+(?P<code>\S+)\s+[—\-]\s+(?P<title>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_BLOCK = re.compile(
    r"^##\s+Bloco\s+(?P<code>\S+)\s+[—\-]\s+(?P<title>.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_PURPOSE = re.compile(r"^\*\*Finalidade:\*\*\s*(.+)$", re.MULTILINE)
_BULLET = re.compile(r"^-\s+(.+)$", re.MULTILINE)


@dataclass
class ParsedPoint:
    text: str


@dataclass
class ParsedBlock:
    code: str
    ordinal: int
    title: str
    development_points: list[ParsedPoint] = field(default_factory=list)


@dataclass
class ParsedFascicle:
    code: str
    ordinal: int
    title: str
    purpose: str = ""
    blocks: list[ParsedBlock] = field(default_factory=list)


@dataclass
class ParsedStructureInventory:
    fascicles: list[ParsedFascicle] = field(default_factory=list)

    @property
    def fascicle_count(self) -> int:
        return len(self.fascicles)

    @property
    def block_count(self) -> int:
        return sum(len(f.blocks) for f in self.fascicles)

    @property
    def point_count(self) -> int:
        return sum(len(b.development_points) for f in self.fascicles for b in f.blocks)


def _ordinal_from_code(code: str) -> int:
    digits = re.findall(r"\d+", code)
    if not digits:
        return 0
    return int(digits[-1])


def parse_generic_structure_inventory(text: str) -> ParsedStructureInventory:
    fascicle_spans = list(_FASCICLE.finditer(text))
    if not fascicle_spans:
        raise ValueError("Nenhum fascículo encontrado (# Fascículo CODE — título).")

    fascicles: list[ParsedFascicle] = []
    for i, match in enumerate(fascicle_spans):
        start = match.start()
        end = fascicle_spans[i + 1].start() if i + 1 < len(fascicle_spans) else len(text)
        section = text[start:end]
        code = match.group("code").strip()
        title = match.group("title").strip()
        purpose_m = _PURPOSE.search(section)
        purpose = purpose_m.group(1).strip() if purpose_m else ""

        blocks: list[ParsedBlock] = []
        block_spans = list(_BLOCK.finditer(section))
        for j, bmatch in enumerate(block_spans):
            bstart = bmatch.start()
            bend = block_spans[j + 1].start() if j + 1 < len(block_spans) else len(section)
            bsec = section[bstart:bend]
            bcode = bmatch.group("code").strip()
            btitle = bmatch.group("title").strip()
            points = [ParsedPoint(text=m.group(1).strip()) for m in _BULLET.finditer(bsec) if m.group(1).strip()]
            blocks.append(
                ParsedBlock(
                    code=bcode,
                    ordinal=_ordinal_from_code(bcode) or (j + 1),
                    title=btitle,
                    development_points=points,
                )
            )

        fascicles.append(
            ParsedFascicle(
                code=code,
                ordinal=_ordinal_from_code(code) if _ordinal_from_code(code) else (i + 1),
                title=title,
                purpose=purpose,
                blocks=blocks,
            )
        )

    return ParsedStructureInventory(fascicles=fascicles)