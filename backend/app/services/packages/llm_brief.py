from __future__ import annotations

from typing import Any

from app.services.packages.package_guidance import (
    CANONICAL_BRIEF_OBJECTIVES,
    PACKAGE_ANTI_PATTERNS,
    USER_CONTRIBUTION_HINTS,
)


def build_llm_brief(
    *,
    scope_kind: str,
    export_id: str,
    display_code: str | None,
    user_notes: str | None,
) -> dict[str, Any]:
    notes = (user_notes or "").strip()
    brief = {
        "version": "1",
        "scope_kind": scope_kind,
        "export_id": export_id,
        "display_code": display_code or "",
        "user_notes": notes,
        "objectives": list(CANONICAL_BRIEF_OBJECTIVES),
        "anti_patterns": list(PACKAGE_ANTI_PATTERNS),
        "references": ["rules", "llm_shapes.collections", "llm_shapes.anti_patterns"],
    }
    brief["suggested_prompt"] = format_brief_for_clipboard(brief)
    return brief


def format_brief_for_clipboard(brief: dict[str, Any]) -> str:
    lines: list[str] = []
    scope = brief.get("scope_kind") or ""
    export_id = brief.get("export_id") or ""
    code = brief.get("display_code") or ""
    notes = (brief.get("user_notes") or "").strip()

    lines.append("=== GET-PACKAGE — instruções para a LLM externa ===")
    lines.append("")
    lines.append("## O seu contributo (preencha antes de enviar)")
    if notes:
        lines.append(notes)
    else:
        lines.append("(ainda vazio — acrescente abaixo ou na conversa antes de executar)")
        for hint in USER_CONTRIBUTION_HINTS:
            lines.append(f"- {hint}")
    lines.append("")
    lines.append("## Tarefa")
    lines.append(
        f"Anexe o ficheiro JSON GET-PACKAGE exportado ({export_id}"
        + (f", âmbito {code}" if code else "")
        + f", scope {scope}). "
        "Devolva o ficheiro JSON GET-PACKAGE **completo**, mesmo export_id e schema GET-PACKAGE 1.0.0."
    )
    lines.append("")
    lines.append("## Comportamento")
    for obj in brief.get("objectives") or CANONICAL_BRIEF_OBJECTIVES:
        lines.append(f"- {obj}")
    lines.append("")
    lines.append("## Anti-padrões (rejeição no importador)")
    for ap in brief.get("anti_patterns") or PACKAGE_ANTI_PATTERNS:
        lines.append(f"- {ap}")
    lines.append("")
    lines.append("## Referências no JSON anexo")
    lines.append("- rules + rules_hash: não alterar")
    lines.append("- llm_shapes: tipos e exemplos por coleção")
    lines.append("- llm_brief: esta mensagem (pode omitir na devolução)")
    return "\n".join(lines)