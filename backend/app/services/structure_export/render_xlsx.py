from __future__ import annotations

import json
from typing import Any

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from app.domain.document_lexicon import title_with_production_label
from app.schemas.structure_export import (
    DocumentStructureSnapshotV1,
    PointFullSnapshot,
    PointSummarySnapshot,
    StructureTreeNodeSnapshot,
)
from app.services.workbook.xlsx_writer import workbook_to_bytes, write_leitura_sheet

SHEET_LEITURA = "00_Leitura"
SHEET_ESTRUTURA = "Estrutura"
SHEET_PONTOS = "Pontos"

ESTRUTURA_HEADERS_BASE = [
    "profundidade",
    "tipo",
    "codigo",
    "titulo",
    "titulo_producao",
    "codigo_pai",
]
ESTRUTURA_HEADERS_MODEL = ["objectivo", "ambito", "estado_bloco"]

PONTOS_HEADERS_SUMMARY = [
    "codigo_bloco",
    "ordem",
    "titulo",
    "estado",
    "llm_freedom",
    "must_include",
    "questoes_abertas",
    "criterios_aceitacao",
    "premissas",
]

PONTOS_HEADERS_FULL = [
    "codigo_bloco",
    "ordem",
    "titulo",
    "estado",
    "llm_freedom",
    "ideia_central",
    "resultado_pretendido",
    "premissas",
]


def _write_header_row(ws: Worksheet, headers: list[str], *, freeze: bool = True) -> None:
    for col, label in enumerate(headers, start=1):
        ws.cell(row=1, column=col, value=label)
    if freeze:
        ws.freeze_panes = "A2"
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18


def _premises_text(premises: list[dict[str, Any]]) -> str:
    return "; ".join(str(p.get("statement", "")).strip() for p in premises if p.get("statement"))


def _walk_estrutura(
    node: StructureTreeNodeSnapshot,
    rows: list[list[Any]],
    *,
    parent_code: str | None,
    include_block_model: bool,
) -> None:
    if node.node_type == "project":
        for child in node.children:
            _walk_estrutura(child, rows, parent_code=None, include_block_model=include_block_model)
        return

    production_title = title_with_production_label(
        node.node_type, node.display_code or "", node.title
    )
    row: list[Any] = [
        node.depth,
        node.node_type,
        node.display_code,
        node.title,
        production_title,
        parent_code or "",
    ]
    if include_block_model:
        bm = node.block_model
        if bm and node.node_type == "block":
            row.extend([bm.objective.strip(), bm.scope.strip(), bm.block_status])
        else:
            row.extend(["", "", ""])
    rows.append(row)
    child_parent = node.display_code or parent_code
    for child in node.children:
        _walk_estrutura(child, rows, parent_code=child_parent, include_block_model=include_block_model)


def _collect_points(
    node: StructureTreeNodeSnapshot,
    points_rows: list[list[Any]],
    *,
    block_code: str | None,
    point_detail: str,
    include_premises: bool,
) -> None:
    code = block_code
    if node.node_type == "block":
        code = node.display_code or block_code

    if node.node_type == "block" and node.points:
        for p in node.points:
            if isinstance(p, PointFullSnapshot):
                premises = _premises_text(p.premises) if include_premises and p.premises else ""
                points_rows.append(
                    [
                        code or "",
                        p.order,
                        p.title,
                        p.status,
                        p.llm_freedom,
                        p.core_idea.strip(),
                        p.intended_outcome.strip(),
                        premises,
                    ]
                )
            else:
                points_rows.append(
                    [
                        code or "",
                        p.order,
                        p.title,
                        p.status,
                        p.llm_freedom,
                        p.must_include_count,
                        p.open_questions_count,
                        p.acceptance_criteria_count,
                        "",
                    ]
                )

    for child in node.children:
        _collect_points(
            child,
            points_rows,
            block_code=code,
            point_detail=point_detail,
            include_premises=include_premises,
        )


def render_xlsx(snapshot: DocumentStructureSnapshotV1) -> bytes:
    wb = Workbook()
    default = wb.active
    wb.remove(default)

    ws_leitura = wb.create_sheet(SHEET_LEITURA)
    context_rows = [
        ("Projecto", snapshot.project_name),
        ("Raiz", f"{snapshot.root_display_code or 'projecto completo'} — {snapshot.root_title}"),
        ("Exportado", snapshot.exported_at),
        ("Utilizador", snapshot.exported_by),
        (
            "Opções",
            json.dumps(
                {
                    "include_block_model": snapshot.options.include_block_model,
                    "point_detail": snapshot.options.point_detail,
                    "include_point_premises": snapshot.options.include_point_premises,
                    "format": snapshot.options.format,
                },
                ensure_ascii=False,
            ),
        ),
        (
            "Reimportação",
            "Este ficheiro é só leitura/revisão. Para alterar a base use o ecrã Workbook (GET) ou GET-PACKAGE.",
        ),
    ]
    write_leitura_sheet(
        ws_leitura,
        title="Exportação estrutural GET — não reimportável",
        subtitle=snapshot.project_name,
        context_rows=context_rows,
    )

    ws_estrutura = wb.create_sheet(SHEET_ESTRUTURA)
    include_model = snapshot.options.include_block_model
    headers = ESTRUTURA_HEADERS_BASE + (ESTRUTURA_HEADERS_MODEL if include_model else [])
    _write_header_row(ws_estrutura, headers)
    estrutura_rows: list[list[Any]] = []
    _walk_estrutura(
        snapshot.tree,
        estrutura_rows,
        parent_code=None,
        include_block_model=include_model,
    )
    for row_idx, row in enumerate(estrutura_rows, start=2):
        for col_idx, value in enumerate(row, start=1):
            ws_estrutura.cell(row=row_idx, column=col_idx, value=value)

    point_detail = snapshot.options.point_detail
    if point_detail != "none":
        ws_pontos = wb.create_sheet(SHEET_PONTOS)
        full = point_detail == "full"
        point_headers = PONTOS_HEADERS_FULL if full else PONTOS_HEADERS_SUMMARY
        _write_header_row(ws_pontos, point_headers)
        points_rows: list[list[Any]] = []
        _collect_points(
            snapshot.tree,
            points_rows,
            block_code=None,
            point_detail=point_detail,
            include_premises=snapshot.options.include_point_premises and full,
        )
        for row_idx, row in enumerate(points_rows, start=2):
            for col_idx, value in enumerate(row, start=1):
                ws_pontos.cell(row=row_idx, column=col_idx, value=value)

    return workbook_to_bytes(wb)