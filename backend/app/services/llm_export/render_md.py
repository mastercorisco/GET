from __future__ import annotations

from typing import Any


def render_llm_export_md(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    ge = payload.get("get_export") or {}
    block = payload.get("block") or {}
    project = payload.get("project") or {}
    fascicle = payload.get("fascicle") or {}

    display = block.get("display_code") or block.get("id", "")
    title = block.get("title") or ""
    lines.append(f"# {display} — {title}")
    lines.append("")
    lines.append("Documento derivado para leitura humana. **Não reimportável.**")
    lines.append("")

    lines.append("## Projecto")
    lines.append(f"- **Nome:** {project.get('name', '')}")
    if project.get("code"):
        lines.append(f"- **Código:** {project.get('code')}")
    if project.get("owner"):
        lines.append(f"- **Entidade:** {project.get('owner')}")
    lines.append("")

    lines.append("## Fascículo")
    lines.append(f"- **{fascicle.get('display_code', '')}** — {fascicle.get('title', '')}")
    if fascicle.get("purpose"):
        lines.append(f"- **Âmbito:** {fascicle.get('purpose')}")
    lines.append("")

    lines.append("## Bloco")
    if block.get("purpose"):
        lines.append(f"**Objectivo:** {block['purpose']}")
        lines.append("")
    scope = block.get("scope") or {}
    if scope.get("narrative"):
        lines.append(scope["narrative"])
        lines.append("")
    if scope.get("includes"):
        lines.append("**Inclui:**")
        for item in scope["includes"]:
            lines.append(f"- {item}")
        lines.append("")
    if scope.get("excludes"):
        lines.append("**Exclui:**")
        for item in scope["excludes"]:
            lines.append(f"- {item}")
        lines.append("")

    units = payload.get("knowledge_units") or []
    if units:
        lines.append("## Unidades de conhecimento")
        for ku in units:
            lines.append(f"### {ku.get('title', '')} ({ku.get('type', '')})")
            if ku.get("statement"):
                lines.append(ku["statement"])
            lines.append("")

    prep = payload.get("preparation") or {}
    points = prep.get("development_points") or []
    if points:
        lines.append("## Pontos de desenvolvimento")
        for point in points:
            order = point.get("order", "")
            lines.append(f"### {order}. {point.get('title') or 'Sem título'}")
            if point.get("core_idea"):
                lines.append(point["core_idea"])
            lines.append("")

    premises = prep.get("applicable_premises") or []
    if premises:
        lines.append("## Premissas aplicáveis")
        for prem in premises:
            imp = prem.get("importance", "")
            lines.append(f"- ({imp}) {prem.get('statement', '')}")
        lines.append("")

    open_points = payload.get("open_points") or []
    if open_points:
        lines.append("## Questões em aberto")
        for op in open_points:
            lines.append(f"- {op.get('question', '')}")
        lines.append("")

    rules = payload.get("generation_rules") or {}
    must = rules.get("must") or []
    if must:
        lines.append("## Regras de geração (resumo)")
        for rule in must[:6]:
            lines.append(f"- {rule}")
        lines.append("")

    lines.append(f"_Exportado GET-LLM {ge.get('schema_version', '')} em {ge.get('generated_at', '')}_")
    return "\n".join(lines) + "\n"