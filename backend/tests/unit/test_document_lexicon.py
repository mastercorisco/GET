from __future__ import annotations

from app.domain.document_lexicon import (
    label_pt,
    load_text_production_lexicon,
    merge_generation_rules_with_lexicon,
    title_with_production_label,
)


def test_load_text_production_lexicon_labels() -> None:
    lex = load_text_production_lexicon()
    assert lex["labels"]["fascicle"] == "Capítulo"
    assert lex["labels"]["block"] == "Ponto"
    assert label_pt("fascicle") == "Capítulo"


def test_merge_generation_rules_includes_lexicon() -> None:
    rules = merge_generation_rules_with_lexicon({"generation_rules": {"must": ["x"]}})
    assert "document_lexicon" in rules
    assert rules["document_lexicon"]["labels"]["block"] == "Ponto"
    assert rules["must"] == ["x"]


def test_title_with_production_label() -> None:
    t = title_with_production_label("fascicle", "F01", "Título")
    assert t.startswith("Capítulo")
    assert "F01" in t