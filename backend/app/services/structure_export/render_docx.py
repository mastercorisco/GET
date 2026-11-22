from __future__ import annotations

import json
from io import BytesIO

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph

from app.domain.document_lexicon import label_pt, title_with_production_label
from app.schemas.structure_export import (
    DocumentStructureSnapshotV1,
    PointFullSnapshot,
    PointSummarySnapshot,
    StructureTreeNodeSnapshot,
)

LIST_NUMBER_STYLE = "List Number"


def _heading_level(depth: int) -> int:
    return min(max(depth + 1, 2), 6)


def _restart_list_numbering(paragraph: Paragraph) -> None:
    """Reinicia numeração Word no primeiro item de cada lista de pontos."""
    p_pr = paragraph._p.get_or_add_pPr()
    num_pr = p_pr.get_or_add_numPr()
    for child in list(num_pr):
        num_pr.remove(child)
    ilvl = num_pr.makeelement(qn("w:ilvl"), {qn("w:val"): "0"})
    num_id = num_pr.makeelement(qn("w:numId"), {qn("w:val"): "1"})
    num_pr.append(ilvl)
    num_pr.append(num_id)


def _add_indented_note(document: Document, prefix: str, text: str) -> None:
    para = document.add_paragraph(f"{prefix}{text}")
    para.paragraph_format.left_indent = Cm(1.0)


def _add_points(document: Document, points: list[PointSummarySnapshot] | list[PointFullSnapshot] | None) -> None:
    if not points:
        return
    for idx, p in enumerate(points):
        title = p.title.strip()
        para = document.add_paragraph(title, style=LIST_NUMBER_STYLE)
        if idx == 0:
            _restart_list_numbering(para)
        if isinstance(p, PointFullSnapshot):
            if p.core_idea.strip():
                _add_indented_note(document, "Ideia central: ", p.core_idea.strip())
            if p.intended_outcome.strip():
                _add_indented_note(document, "Resultado: ", p.intended_outcome.strip())
            if p.premises:
                document.add_paragraph("Premissas:")
                for pr in p.premises:
                    statement = str(pr.get("statement", "")).strip()
                    if statement:
                        document.add_paragraph(statement, style="List Bullet")


def _walk_node(document: Document, node: StructureTreeNodeSnapshot) -> None:
    if node.node_type == "project":
        for child in node.children:
            _walk_node(document, child)
        return

    heading_title = title_with_production_label(
        node.node_type, node.display_code or "", node.title
    )
    document.add_heading(heading_title, level=_heading_level(node.depth))

    if node.node_type == "block" and node.block_model:
        bm = node.block_model
        if bm.objective.strip():
            document.add_paragraph(f"Objectivo: {bm.objective.strip()}")
        if bm.scope.strip():
            document.add_paragraph(f"Âmbito: {bm.scope.strip()}")
        if bm.target_output:
            document.add_paragraph("Resultado pretendido:")
            document.add_paragraph(json.dumps(bm.target_output, ensure_ascii=False, indent=2))
        _add_points(document, node.points)
    elif node.points:
        dev_label = label_pt("development_point") or "Ponto de desenvolvimento"
        document.add_heading(f"{dev_label}s", level=min(_heading_level(node.depth) + 1, 6))
        _add_points(document, node.points)

    for child in node.children:
        _walk_node(document, child)


def render_docx(snapshot: DocumentStructureSnapshotV1) -> bytes:
    document = Document()
    document.add_heading(f"Estrutura documental — {snapshot.project_name}", level=0)

    notice = document.add_paragraph()
    notice.add_run("Documento derivado para leitura humana. ").bold = False
    run = notice.add_run("Não reimportável.")
    run.bold = True

    document.add_paragraph(f"Exportado: {snapshot.exported_at}")
    document.add_paragraph(f"Utilizador: {snapshot.exported_by}")
    document.add_paragraph(
        f"Raiz: {snapshot.root_display_code or 'projecto completo'} — {snapshot.root_title}"
    )
    document.add_paragraph(
        f"Opções: modelo_do_bloco={'sim' if snapshot.options.include_block_model else 'não'}, "
        f"pontos={snapshot.options.point_detail}"
    )

    document.add_paragraph("—" * 40).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    _walk_node(document, snapshot.tree)

    buffer = BytesIO()
    document.save(buffer)
    return buffer.getvalue()