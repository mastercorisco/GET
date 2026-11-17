from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]

_DEFAULT: dict[str, Any] = {
    "profile": "text_production_pt",
    "labels": {
        "fascicle": "Capítulo",
        "block": "Ponto",
        "development_point": "Ponto de desenvolvimento",
    },
    "technical_keys_note": (
        "As chaves JSON fascicle, block e development_points são identificadores GET; "
        "ao redigir texto use os rótulos deste glossário."
    ),
    "llm_glossary": (
        "Nas exportações GET-LLM, os objectos fascicle e block representam, na produção de texto, "
        "capítulo e ponto, respectivamente; development_points são pontos de desenvolvimento."
    ),
}


@lru_cache(maxsize=1)
def load_text_production_lexicon() -> dict[str, Any]:
    path = _REPO_ROOT / "catalogs" / "document_lexicon.text_production.pt-PT.json"
    if not path.is_file():
        return dict(_DEFAULT)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return dict(_DEFAULT)
    return data


def label_pt(node_type: str) -> str | None:
    labels = load_text_production_lexicon().get("labels") or {}
    if not isinstance(labels, dict):
        return None
    return labels.get(node_type)


def document_lexicon_for_export() -> dict[str, Any]:
    lex = load_text_production_lexicon()
    return {
        "profile": lex.get("profile", "text_production_pt"),
        "labels": dict(lex.get("labels") or {}),
        "llm_glossary": lex.get("llm_glossary", ""),
        "technical_keys_note": lex.get("technical_keys_note", ""),
    }


def merge_generation_rules_with_lexicon(catalog: dict[str, Any]) -> dict[str, Any]:
    rules = dict(catalog.get("generation_rules") or {})
    rules["document_lexicon"] = document_lexicon_for_export()
    return rules


def annotate_node_role(row: dict[str, Any], node_type: str) -> dict[str, Any]:
    """Add text_production_label_pt when node_type is fascicle or block."""
    out = dict(row)
    label = label_pt(node_type)
    if label:
        out["text_production_label_pt"] = label
    return out


def title_with_production_label(node_type: str, display_code: str, title: str) -> str:
    """Visible title for MD/PDF/XMind."""
    label = label_pt(node_type)
    code_part = f"{display_code} — " if display_code else ""
    base = f"{code_part}{title}".strip()
    if label and node_type in ("fascicle", "block"):
        return f"{label} {base}"
    return base