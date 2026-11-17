from __future__ import annotations

import io
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.domain.document_lexicon import title_with_production_label
from app.schemas.structure_export import DocumentStructureSnapshotV1, PointFullSnapshot, StructureTreeNodeSnapshot


def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _plain_para(text: str, style) -> Paragraph:
    return Paragraph(_xml_escape(text), style)


def _rich_para(markup: str, style) -> Paragraph:
    """ReportLab mini-HTML; user text inside markup must already be escaped."""
    return Paragraph(markup, style)


def _heading_style_key(node: StructureTreeNodeSnapshot) -> str:
    if node.node_type == "fascicle":
        return "fascicle"
    if node.node_type == "block":
        return "block"
    if node.node_type in ("section", "subsection"):
        return "section"
    level = min(max(node.depth + 1, 2), 4)
    return f"h{level}"


def _point_markup(p) -> str:
    title = _xml_escape(p.title.strip())
    if isinstance(p, PointFullSnapshot):
        idea = _xml_escape(p.core_idea.strip()[:500])
        if idea:
            return f"<b>{p.order}. {title}</b> — {idea}"
        return f"<b>{p.order}. {title}</b>"
    return f"<b>{p.order}. {title}</b>"


def _walk_node(
    node: StructureTreeNodeSnapshot,
    story: list,
    styles: dict,
) -> None:
    if node.node_type == "project":
        for child in node.children:
            _walk_node(child, story, styles)
        return

    style_key = _heading_style_key(node)
    style = styles.get(style_key, styles["body"])
    visible = title_with_production_label(node.node_type, node.display_code or "", node.title)
    story.append(_rich_para(f"<b>{_xml_escape(visible)}</b>", style))
    story.append(Spacer(1, 0.12 * cm))

    if node.block_model:
        bm = node.block_model
        point_style = styles["point"]
        if bm.objective.strip():
            story.append(
                _rich_para(
                    f"<b>Objectivo:</b> {_xml_escape(bm.objective.strip())}",
                    point_style,
                )
            )
        if bm.scope.strip():
            story.append(
                _rich_para(f"<b>Âmbito:</b> {_xml_escape(bm.scope.strip())}", point_style)
            )
        if bm.target_output:
            story.append(_rich_para("<b>Resultado pretendido:</b>", point_style))
            story.append(_plain_para(json.dumps(bm.target_output, ensure_ascii=False), styles["code"]))

    if node.points:
        for p in node.points:
            story.append(_rich_para(_point_markup(p), styles["point"]))
        story.append(Spacer(1, 0.08 * cm))

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
        "fascicle": ParagraphStyle(
            "FascicleHeading",
            parent=base["Heading2"],
            backColor=colors.HexColor("#e8e8e8"),
            borderPadding=6,
            spaceBefore=10,
            spaceAfter=4,
            leftIndent=0,
        ),
        "block": ParagraphStyle(
            "BlockHeading",
            parent=base["Heading3"],
            leftIndent=0.75 * cm,
            spaceBefore=6,
            spaceAfter=2,
        ),
        "section": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading4"],
            leftIndent=1.1 * cm,
            spaceBefore=4,
        ),
        "body": base["BodyText"],
        "point": ParagraphStyle(
            "DevelopmentPoint",
            parent=base["BodyText"],
            leftIndent=1.35 * cm,
            spaceBefore=2,
            leading=13,
        ),
        "code": ParagraphStyle("Code", parent=base["Code"], fontSize=8, leading=10, leftIndent=1.35 * cm),
    }
    story: list = []
    story.append(_plain_para(f"Estrutura documental — {snapshot.project_name}", styles["h1"]))
    story.append(
        _plain_para(
            "Documento derivado. Não reimportável. "
            f"Exportado {snapshot.exported_at} por {snapshot.exported_by}.",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    _walk_node(snapshot.tree, story, styles)
    doc.build(story)
    return buffer.getvalue()