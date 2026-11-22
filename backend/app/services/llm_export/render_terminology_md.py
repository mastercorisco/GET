from __future__ import annotations

from typing import Any


def render_terminology_glossary_md(
    snapshot: dict[str, Any],
    *,
    export_id: str,
    profile: str,
    generated_at: str,
) -> str:
    project = snapshot.get("project") or {}
    lines = [
        "# Glossário técnico (Terminologia GET)",
        "",
        "Documento derivado para leitura humana e LLM. **Não reimportável.**",
        "",
        f"_Pacote {export_id} · perfil `{profile}` · {generated_at}_",
        "",
        "Use **termo preferencial** na redação. Respeite **evitar** e **overrides** do projecto.",
        "Distinto do «Glossário (produção de texto)» (capítulo/ponto estrutural).",
        "",
        f"## Projecto: {project.get('name', '')}",
        "",
    ]

    lib = snapshot.get("library_terms") or []
    if lib:
        lines.append("## Biblioteca (partilhado)")
        lines.append("")
        for row in lib:
            lines.extend(_term_block(row))
        lines.append("")

    proj = snapshot.get("project_terms") or []
    if proj:
        lines.append("## Termos específicos do projecto")
        lines.append("")
        for row in proj:
            lines.extend(_term_block(row))
        lines.append("")

    overrides = snapshot.get("project_overrides") or []
    if overrides:
        lines.append("## Overrides no projecto")
        lines.append("")
        for row in overrides:
            lines.append(f"### {row.get('preferred_term', '')}")
            lines.append(f"- **Conceito:** `{row.get('concept_id', '')[:8]}…`")
            if row.get("legacy_term"):
                lines.append(f"- **Legado aceite:** {row['legacy_term']}")
            if row.get("avoid_in_project"):
                lines.append("- **Evitar no projecto:** sim")
            if row.get("usage_note"):
                lines.append(f"- **Nota:** {row['usage_note']}")
            lines.append("")

    if not lib and not proj and not overrides:
        lines.append("_Sem entradas de terminologia registadas._")
        lines.append("")

    return "\n".join(lines)


def _term_block(row: dict[str, Any]) -> list[str]:
    title = row.get("preferred_term") or "(sem termo)"
    lines = [f"### {title}"]
    if row.get("acronym"):
        lines.append(f"- **Sigla:** {row['acronym']}")
    lines.append(f"- **Definição:** {row.get('definition', '')}")
    if row.get("synonyms"):
        lines.append(f"- **Sinónimos:** {', '.join(row['synonyms'])}")
    if row.get("avoid_terms"):
        lines.append(f"- **Evitar:** {', '.join(row['avoid_terms'])}")
    if row.get("technical_translation"):
        lines.append(f"- **Tradução técnica:** {row['technical_translation']}")
    if row.get("domain"):
        lines.append(f"- **Domínio:** {row['domain']}")
    if row.get("notes"):
        lines.append(f"- **Notas:** {row['notes']}")
    lines.append(f"- _id:_ `{row.get('id', '')}`")
    lines.append("")
    return lines