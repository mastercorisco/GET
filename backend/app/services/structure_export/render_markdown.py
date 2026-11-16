from __future__ import annotations

import json
from typing import Iterable

from app.schemas.structure_export import (
    DocumentStructureSnapshotV1,
    PointFullSnapshot,
    PointSummarySnapshot,
    StructureTreeNodeSnapshot,
)


def _heading_level(depth: int) -> str:
    level = min(max(depth + 1, 2), 6)
    return "#" * level


def _format_points_md(points: list[PointSummarySnapshot] | list[PointFullSnapshot] | None) -> list[str]:
    if not points:
        return []
    lines: list[str] = []
    for p in points:
        if isinstance(p, PointFullSnapshot):
            lines.append(f"- **{p.order}. {p.title}** (`{p.status}`, {p.llm_freedom})")
            if p.core_idea.strip():
                lines.append(f"  - Ideia central: {p.core_idea.strip()}")
            if p.intended_outcome.strip():
                lines.append(f"  - Resultado: {p.intended_outcome.strip()}")
            if p.premises:
                lines.append("  - Premissas:")
                for pr in p.premises:
                    lines.append(f"    - {pr.get('statement', '')}")
        else:
            lines.append(
                f"- **{p.order}. {p.title}** (`{p.status}`) — "
                f"must={p.must_include_count}, abertos={p.open_questions_count}, critérios={p.acceptance_criteria_count}"
            )
    return lines


def _walk_node(node: StructureTreeNodeSnapshot, lines: list[str]) -> None:
    code_part = f"{node.display_code} — " if node.display_code else ""
    lines.append(f"{_heading_level(node.depth)} {code_part}{node.title}")
    lines.append("")
    if node.node_type == "block" and node.block_model:
        bm = node.block_model
        if bm.objective.strip():
            lines.append(f"**Objectivo:** {bm.objective.strip()}")
            lines.append("")
        if bm.scope.strip():
            lines.append(f"**Âmbito:** {bm.scope.strip()}")
            lines.append("")
        if bm.target_output:
            lines.append("**Resultado pretendido:**")
            lines.append("```json")
            lines.append(json.dumps(bm.target_output, ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")
        lines.extend(_format_points_md(node.points))
        if node.points:
            lines.append("")
    elif node.points:
        lines.append("### Pontos de desenvolvimento")
        lines.extend(_format_points_md(node.points))
        lines.append("")
    for child in node.children:
        _walk_node(child, lines)


def render_markdown(snapshot: DocumentStructureSnapshotV1) -> str:
    lines: list[str] = [
        f"# Estrutura documental — {snapshot.project_name}",
        "",
        "> Documento derivado para leitura humana. **Não reimportável.**",
        "",
        f"- Exportado: {snapshot.exported_at}",
        f"- Utilizador: {snapshot.exported_by}",
        f"- Raiz: {snapshot.root_display_code or 'projecto completo'} — {snapshot.root_title}",
        f"- Opções: bloco={'sim' if snapshot.options.include_block_model else 'não'}, "
        f"pontos={snapshot.options.point_detail}",
        "",
        "---",
        "",
    ]
    _walk_node(snapshot.tree, lines)
    return "\n".join(lines).rstrip() + "\n"