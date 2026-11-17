from __future__ import annotations

from typing import Any

from app.services.packages.package_guidance import (
    BRIEF_READ_ORDER,
    BRIEF_SELF_CHECK,
    BRIEF_WORKFLOW,
    CANONICAL_BRIEF_OBJECTIVES,
    PACKAGE_ANTI_PATTERNS,
    SCOPE_TASK_FOCUS,
    USER_CONTRIBUTION_HINTS,
    USER_CONTRIBUTION_TEMPLATE,
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

    lines.append("Papel: editor técnico GET-PACKAGE — devolver só JSON válido, pronto a reimportar na app GET.")
    lines.append("")
    lines.append("---")
    lines.append("## Contexto do utilizador (autoridade humana)")
    if notes:
        lines.append(notes)
    else:
        lines.append("Substitua o bloco abaixo pelo seu contexto antes de executar:")
        lines.append("")
        lines.append(USER_CONTRIBUTION_TEMPLATE.strip())
        lines.append("")
        lines.append("Indicadores úteis:")
        for hint in USER_CONTRIBUTION_HINTS:
            lines.append(f"- {hint}")
    lines.append("---")
    lines.append("")
    lines.append("## Pacote anexo")
    scope_line = (
        f"Ficheiro GET-PACKAGE: export_id={export_id}, scope={scope}"
        + (f", código documental {code}" if code else "")
        + "."
    )
    lines.append(scope_line)
    focus = SCOPE_TASK_FOCUS.get(scope)
    if focus:
        lines.append(focus)
    lines.append(
        "Tarefa: editar o payload conforme abaixo e devolver o JSON GET-PACKAGE 1.0.0 COMPLETO "
        f"(mesmo export_id={export_id}). Saída = ficheiro JSON único; sem narrativa fora do JSON."
    )
    lines.append("")
    lines.append("## Ordem de leitura no JSON")
    for i, step in enumerate(BRIEF_READ_ORDER, start=1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("## Regras de edição")
    for obj in brief.get("objectives") or CANONICAL_BRIEF_OBJECTIVES:
        lines.append(f"- {obj}")
    lines.append("")
    lines.append("## Procedimento")
    for i, step in enumerate(BRIEF_WORKFLOW, start=1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("## Anti-padrões (causam rejeição no importador)")
    for ap in brief.get("anti_patterns") or PACKAGE_ANTI_PATTERNS:
        lines.append(f"- {ap}")
    lines.append("")
    lines.append("## Autoverificação antes de entregar")
    for item in BRIEF_SELF_CHECK:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## Campos do envelope")
    lines.append("- rules + rules_hash: copiar sem alteração")
    lines.append("- llm_shapes: guia de tipos (não precisa de voltar na devolução, mas pode)")
    lines.append("- llm_brief: opcional na devolução")
    return "\n".join(lines)