"""Parser do inventário CTBJ v3 (Markdown)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

FASCICLE_RE = re.compile(r"^## (F\d{2}) — (.+)$")
BLOCK_RE = re.compile(r"^### ((?:F\d{2})_B\d{2}(?:/B\d{2})?) — (.+)$")
FASCICLE_COMPLEMENT_RE = re.compile(r"^### (F\d{2}) — (.+)$")
BULLET_RE = re.compile(r"^- (.+)$")
GENERIC_POINT_PREFIX = "Definir o âmbito, objetivos e fronteiras"


@dataclass
class CatalogPoint:
    text: str


@dataclass
class CatalogBlock:
    code: str
    fascicle_code: str
    ordinal: int
    title: str
    development_points: list[CatalogPoint] = field(default_factory=list)


@dataclass
class CatalogFascicle:
    code: str
    ordinal: int
    title: str
    blocks: list[CatalogBlock] = field(default_factory=list)


@dataclass
class ComplementRule:
    """Substituição de pontos genéricos por matérias de domínio."""

    target_block_codes: list[str] = field(default_factory=list)
    target_fascicle_code: str | None = None
    replace: bool = True
    development_points: list[str] = field(default_factory=list)


@dataclass
class ParsedCatalog:
    fascicles: list[CatalogFascicle]
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


def _strip_period(text: str) -> str:
    return text[:-1] if text.endswith(".") else text


def _fascicle_ordinal(code: str) -> int:
    return int(code[1:])


def _block_ordinal(code: str) -> int:
    return int(code.split("_B")[1])


def _resolve_block_codes(raw: str) -> list[str]:
    raw = raw.strip()
    if "/" in raw and "_B" in raw:
        parts = raw.split("/")
        first = parts[0]
        base = first.rsplit("_B", 1)[0]
        if parts[1].startswith("B"):
            return [first, f"{base}_B{parts[1][1:]}"]
    if "_B" in raw:
        return [raw]
    return []


def is_generic_block(block: CatalogBlock) -> bool:
    if not block.development_points:
        return False
    return block.development_points[0].text.startswith(GENERIC_POINT_PREFIX)


def apply_complements_to_catalog(parsed: ParsedCatalog) -> None:
    """Aplica regras de complemento (substituição de templates genéricos)."""
    by_block: dict[str, CatalogBlock] = {}
    by_fascicle: dict[str, CatalogFascicle] = {f.code: f for f in parsed.fascicles}
    for fascicle in parsed.fascicles:
        for block in fascicle.blocks:
            by_block[block.code] = block

    for rule in parsed.complements:
        texts = [CatalogPoint(text=_strip_period(t)) for t in rule.development_points]
        if rule.target_fascicle_code:
            fascicle = by_fascicle.get(rule.target_fascicle_code)
            if fascicle is None:
                continue
            for block in fascicle.blocks:
                if rule.replace and is_generic_block(block):
                    block.development_points = list(texts)
            continue
        for code in rule.target_block_codes:
            block = by_block.get(code)
            if block is None:
                continue
            if rule.replace:
                block.development_points = list(texts)


def _parse_structure_lines(lines: list[str]) -> list[CatalogFascicle]:
    fascicles: list[CatalogFascicle] = []
    current_fascicle: CatalogFascicle | None = None
    current_block: CatalogBlock | None = None

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("# Estrutura GET CTBJ"):
            continue
        m_fasc = FASCICLE_RE.match(line)
        if m_fasc:
            current_fascicle = CatalogFascicle(
                code=m_fasc.group(1),
                ordinal=_fascicle_ordinal(m_fasc.group(1)),
                title=m_fasc.group(2).strip(),
                blocks=[],
            )
            fascicles.append(current_fascicle)
            current_block = None
            continue
        m_block = BLOCK_RE.match(line)
        if m_block and current_fascicle is not None:
            code = m_block.group(1).split("/")[0]
            fascicle_code = code.split("_")[0]
            current_block = CatalogBlock(
                code=code,
                fascicle_code=fascicle_code,
                ordinal=_block_ordinal(code),
                title=m_block.group(2).strip(),
            )
            current_fascicle.blocks.append(current_block)
            continue
        m_bullet = BULLET_RE.match(line)
        if m_bullet and current_block is not None:
            current_block.development_points.append(
                CatalogPoint(text=_strip_period(m_bullet.group(1).strip()))
            )
    return fascicles


def _parse_complement_lines(lines: list[str]) -> list[ComplementRule]:
    rules: list[ComplementRule] = []
    current: ComplementRule | None = None
    bullets: list[str] = []

    def flush() -> None:
        nonlocal current, bullets
        if current is not None and bullets:
            current.development_points = bullets
            rules.append(current)
        current = None
        bullets = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("## Execução"):
            flush()
            break
        m_block = BLOCK_RE.match(line)
        if m_block:
            flush()
            codes = _resolve_block_codes(m_block.group(1))
            current = ComplementRule(target_block_codes=codes, replace=True)
            continue
        m_fasc = FASCICLE_COMPLEMENT_RE.match(line)
        if m_fasc:
            flush()
            current = ComplementRule(target_fascicle_code=m_fasc.group(1), replace=True)
            continue
        m_bullet = BULLET_RE.match(line)
        if m_bullet and current is not None:
            bullets.append(m_bullet.group(1).strip())

    flush()
    return rules


def parse_ctbj_v3_inventory(text: str, *, apply_complements: bool = False) -> ParsedCatalog:
    """Extrai fascículos, blocos e bullets; complementos opcionais para sync."""
    marker = "## Complementos obrigatórios"
    idx = text.find(marker)
    if idx < 0:
        main_text = text
        complement_text = ""
    else:
        main_text = text[:idx]
        complement_text = text[idx:]

    start = main_text.find("## F01 —")
    if start >= 0:
        main_text = main_text[start:]

    fascicles = _parse_structure_lines(main_text.splitlines())
    complements = _parse_complement_lines(complement_text.splitlines()) if complement_text else []
    parsed = ParsedCatalog(fascicles=fascicles, complements=complements)
    if apply_complements:
        apply_complements_to_catalog(parsed)
    return parsed