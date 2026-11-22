from __future__ import annotations

from typing import Any

from app.domain.document_lexicon import label_pt, load_text_production_lexicon


def _header_banner(ge: dict[str, Any]) -> list[str]:
    return [
        "Documento derivado para leitura humana. **Não reimportável.**",
        "",
        f"_GET-LLM {ge.get('export_type', '')} · {ge.get('schema_version', '')} · {ge.get('generated_at', '')}_",
        "",
    ]


def _glossary_section() -> list[str]:
    lex = load_text_production_lexicon()
    glossary = (lex.get("llm_glossary") or "").strip()
    if not glossary:
        return []
    return ["## Glossário (produção de texto)", glossary, ""]


def _project_section(project: dict[str, Any]) -> list[str]:
    lines = ["## Projecto", f"- **Nome:** {project.get('name', '')}"]
    if project.get("code"):
        lines.append(f"- **Código:** {project.get('code')}")
    if project.get("owner"):
        lines.append(f"- **Entidade:** {project.get('owner')}")
    lines.append("")
    return lines


def render_llm_master_md(payload: dict[str, Any]) -> str:
    ge = payload.get("get_export") or {}
    ch = label_pt("fascicle") or "Capítulo"
    pt = label_pt("block") or "Ponto"
    lines = (
        ["# Pacote GET-LLM — Mestre", ""]
        + _header_banner(ge)
        + _glossary_section()
        + _project_section(payload.get("project") or {})
    )

    term_file = (payload.get("package_terminology_markdown") or "").strip()
    if term_file:
        lines.append("## Glossário técnico (vocabulário)")
        lines.append(
            f"Consultar o ficheiro **`{term_file}`** neste pacote antes de redigir "
            "(termos preferenciais, evitar, overrides)."
        )
        lines.append("")

    lines.append(f"## {ch}s")
    for row in payload.get("fascicle_manifest") or []:
        lines.append(
            f"- **{row.get('display_code', '')}** {row.get('title', '')} "
            f"({row.get('block_count', 0)} {pt.lower()}s) → `{row.get('filename', '')}`"
        )
    lines.append("")

    ki = payload.get("knowledge_index") or []
    if ki:
        lines.append("## Índice de conhecimento (projecto)")
        for row in ki[:30]:
            lines.append(f"- {row.get('code') or row.get('id')}: {row.get('title', '')}")
        if len(ki) > 30:
            lines.append(f"- _… e mais {len(ki) - 30}_")
        lines.append("")

    oq = payload.get("global_open_questions") or []
    if oq:
        lines.append("## Questões abertas (projecto)")
        for row in oq:
            lines.append(f"- {row.get('title', '')}")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_llm_fascicle_md(payload: dict[str, Any]) -> str:
    ge = payload.get("get_export") or {}
    fascicle = payload.get("fascicle") or {}
    ch = label_pt("fascicle") or "Capítulo"
    pt = label_pt("block") or "Ponto"
    dev_label = label_pt("development_point") or "Ponto de desenvolvimento"
    lines = [
        f"# {ch} {fascicle.get('display_code', '')} — {fascicle.get('title', '')}",
        "",
    ] + _header_banner(ge) + _glossary_section() + _project_section(payload.get("project") or {})

    lines.append(f"## {pt}s")
    for row in payload.get("block_summaries") or []:
        mark = "incluído" if row.get("included_in_package") else "sem pontos de desenvolvimento exportáveis"
        lines.append(
            f"- **{row.get('display_code', '')}** {row.get('title', '')} "
            f"({row.get('exportable_point_count', 0)} {dev_label.lower()}; {mark})"
        )
    lines.append("")

    manifest = payload.get("block_manifest") or []
    if manifest:
        lines.append(f"## Ficheiros de {pt.lower()} no pacote")
        for row in manifest:
            lines.append(f"- `{row.get('filename', '')}` — {row.get('display_code', '')}")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_llm_block_md(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    ge = payload.get("get_export") or {}
    block = payload.get("block") or {}
    project = payload.get("project") or {}
    fascicle = payload.get("fascicle") or {}
    ch = label_pt("fascicle") or "Capítulo"
    pt = label_pt("block") or "Ponto"

    display = block.get("display_code") or block.get("id", "")
    title = block.get("title") or ""
    lines.append(f"# {pt} {display} — {title}")
    lines.append("")
    lines.extend(_header_banner(ge))
    lines.extend(_glossary_section())
    lines.extend(_project_section(project))

    lines.append(f"## {ch}")
    lines.append(f"- **{fascicle.get('display_code', '')}** — {fascicle.get('title', '')}")
    if fascicle.get("purpose"):
        lines.append(f"- **Âmbito:** {fascicle.get('purpose')}")
    lines.append("")

    lines.append(f"## {pt}")
    if block.get("purpose"):
        lines.append(f"**Objectivo:** {block['purpose']}")
        lines.append("")
    scope = block.get("scope") or {}
    if scope.get("narrative"):
        lines.append(scope["narrative"])
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

    return "\n".join(lines) + "\n"


def render_llm_export_md(payload: dict[str, Any]) -> str:
    export_type = (payload.get("get_export") or {}).get("export_type", "block")
    if export_type == "project_master":
        return render_llm_master_md(payload)
    if export_type == "fascicle":
        return render_llm_fascicle_md(payload)
    return render_llm_block_md(payload)