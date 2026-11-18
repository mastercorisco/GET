"""Correspondência semântica leve (títulos e textos de pontos)."""

from __future__ import annotations

import re
import unicodedata

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STRIP_CHARS = re.compile(r"[^\w\s]", re.UNICODE)


def normalize_text(value: str) -> str:
    text = value.strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _STRIP_CHARS.sub(" ", text)
    return " ".join(text.split())


def token_set(value: str) -> set[str]:
    return set(_TOKEN_RE.findall(normalize_text(value)))


def token_jaccard(a: str, b: str) -> float:
    sa, sb = token_set(a), token_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def texts_match(a: str, b: str, *, threshold: float = 0.55) -> bool:
    if normalize_text(a) == normalize_text(b):
        return True
    if a.strip().startswith(b.strip()[:40]) or b.strip().startswith(a.strip()[:40]):
        return True
    return token_jaccard(a, b) >= threshold


def best_title_match(
    title: str,
    candidates: list[tuple[str, str]],
    *,
    threshold: float = 0.45,
    used: set[str] | None = None,
) -> tuple[str, float] | None:
    """Devolve (id, score) do melhor candidato único."""
    used = used or set()
    scored: list[tuple[str, float]] = []
    for node_id, cand_title in candidates:
        if node_id in used:
            continue
        score = token_jaccard(title, cand_title)
        if score >= threshold:
            scored.append((node_id, score))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[1], x[0]))
    best_id, best_score = scored[0]
    if len(scored) > 1 and scored[1][1] >= best_score - 0.05:
        return None
    return best_id, best_score