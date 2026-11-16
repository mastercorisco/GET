from __future__ import annotations

import io
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.schemas.structure_export import DocumentStructureSnapshotV1, PointFullSnapshot, StructureTreeNodeSnapshot


def _para(text: str, style) -> Paragraph:
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


def _walk_node(
    node: StructureTreeNodeSnapshot,
    story: list,
    styles: dict,
) -> None:
    level = min(max(node.depth + 1, 2), 4)
    style_key = f"h{level}"
    code = f"{node.display_code} — " if node.display_code else ""
    story.append(_para(f"{code}{node.title}", styles[style_key]))
    story.append(Spacer(1, 0.15 * cm))
    if node.block_model:
        bm = node.block_model
        if bm.objective.strip():
            story.append(_para(f"<b>Objectivo:</b> {bm.objective.strip()}", styles["body"]))
        if bm.scope.strip():
            story.append(_para(f"<b>Âmbito:</b> {bm.scope.strip()}", styles["body"]))
        if bm.target_output:
            story.append(_para("<b>Resultado pretendido:</b>", styles["body"]))
            story.append(_para(json.dumps(bm.target_output, ensure_ascii=False), styles["code"]))
    if node.points:
        for p in node.points:
            if isinstance(p, PointFullSnapshot):
                story.append(
                    _para(
                        f"<b>{p.order}. {p.title}</b> ({p.status}) — {p.core_idea[:500]}",
                        styles["body"],
                    )
                )
            else:
                story.append(_para(f"<b>{p.order}. {p.title}</b> ({p.status})", styles["body"]))
        story.append(Spacer(1, 0.1 * cm))
    for child in node.children:
        _walk_node(child, story, styles)


def render_pdf(snapshot: DocumentStructureSnapshotV1) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=snapshot.project_name)
    base = getSampleStyleSheet()
    styles = {
        "h1": base["Heading1"],
        "h2": base["Heading2"],
        "h3": base["Heading3"],
        "h4": base["Heading4"],
        "body": base["BodyText"],
        "code": ParagraphStyle("Code", parent=base["Code"], fontSize=8, leading=10),
    }
    story: list = []
    story.append(_para(f"Estrutura documental — {snapshot.project_name}", styles["h1"]))
    story.append(
        _para(
            "Documento derivado. Não reimportável. "
            f"Exportado {snapshot.exported_at} por {snapshot.exported_by}.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    _walk_node(snapshot.tree, story, styles)
    doc.build(story)
    return buffer.getvalue()