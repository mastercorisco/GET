from __future__ import annotations

from typing import Any

from app.services.packages.package_guidance import (
    BRIEF_OUTPUT_CONTRACT,
    BRIEF_QUALITY_CRITERIA,
    BRIEF_READ_ORDER,
    BRIEF_SELF_CHECK,
    BRIEF_SHAPE_EXAMPLES,
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
        "version": "2",
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

    lines.append(
        "Actua como editor técnico GET. Input: JSON GET-PACKAGE anexo. "
        "Output OBRIGATÓRIO: apenas o JSON GET-PACKAGE completo actualizado (sem comentários fora do ficheiro)."
    )
    lines.append("")
    lines.append("---")
    lines.append("## Contexto do utilizador (manda sobre o payload)")
    if notes:
        lines.append(notes)
    else:
        lines.append("(Preencha na app ou abaixo antes de executar; o que estiver aqui tem prioridade sobre suposições.)")
        lines.append("")
        lines.append(USER_CONTRIBUTION_TEMPLATE.strip())
        lines.append("")
        lines.append("Campos úteis:")
        for hint in USER_CONTRIBUTION_HINTS:
            lines.append(f"- {hint}")
    lines.append("---")
    lines.append("")
    lines.append("## Identificação do pacote")
    lines.append(
        f"export_id={export_id} | scope={scope}"
        + (f" | código={code}" if code else "")
    )
    focus = SCOPE_TASK_FOCUS.get(scope)
    if focus:
        lines.append(focus)
    lines.append("")
    lines.append("## Contrato de saída")
    for item in BRIEF_OUTPUT_CONTRACT:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Ordem de leitura no JSON anexo")
    for i, step in enumerate(BRIEF_READ_ORDER, start=1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("## Regras de edição")
    for obj in brief.get("objectives") or CANONICAL_BRIEF_OBJECTIVES:
        lines.append(f"- {obj}")
    lines.append("")
    lines.append("## Critérios de qualidade do conteúdo")
    for q in BRIEF_QUALITY_CRITERIA:
        lines.append(f"- {q}")
    lines.append("")
    lines.append("## Procedimento")
    for i, step in enumerate(BRIEF_WORKFLOW, start=1):
        lines.append(f"{i}. {step}")
    lines.append("")
    lines.append("## Forma correcta (exemplos — imitar estrutura, não copiar texto)")
    for ex in BRIEF_SHAPE_EXAMPLES.get(scope, []):
        lines.append(f"- {ex}")
    lines.append("")
    lines.append("## Anti-padrões (importador rejeita)")
    for ap in brief.get("anti_patterns") or PACKAGE_ANTI_PATTERNS:
        lines.append(f"- {ap}")
    lines.append("")
    lines.append("## Autoverificação")
    for item in BRIEF_SELF_CHECK:
        lines.append(f"- [ ] {item}")
    lines.append("")
    lines.append("## Envelope")
    lines.append("- rules + rules_hash: não tocar")
    lines.append("- llm_shapes / llm_brief: opcionais na devolução")
    return "\n".join(lines)