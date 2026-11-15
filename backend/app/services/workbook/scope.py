from __future__ import annotations


def is_reutilizavel(text: str | None) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return "reutiliz" in lowered


def resolve_scope(natureza: str | None) -> str:
    """library quando Natureza implica reutilização; caso contrário project."""
    return "library" if is_reutilizavel(natureza) else "project"