from __future__ import annotations

from app.services.packages.llm_brief import build_llm_brief, format_brief_for_clipboard
from app.services.packages.package_guidance import PACKAGE_ANTI_PATTERNS


def test_format_brief_includes_anti_patterns_and_scope() -> None:
    brief = build_llm_brief(
        scope_kind="block",
        export_id="PKG-BLK-TEST",
        display_code="B01",
        user_notes="",
    )
    text = format_brief_for_clipboard(brief)
    assert "Anti-padrões" in text
    assert "Contrato de saída" in text
    assert "BOM must_include" in text
    assert PACKAGE_ANTI_PATTERNS[0] in text
    assert "PKG-BLK-TEST" in text
    assert "scope=block" in text


def test_user_notes_in_brief() -> None:
    brief = build_llm_brief(
        scope_kind="fascicle",
        export_id="PKG-FASC-F01",
        display_code="F01",
        user_notes="só pontos ready",
    )
    assert brief["user_notes"] == "só pontos ready"
    text = format_brief_for_clipboard(brief)
    assert "só pontos ready" in text
    assert "Contexto do utilizador" in text
    assert "Autoverificação" in text