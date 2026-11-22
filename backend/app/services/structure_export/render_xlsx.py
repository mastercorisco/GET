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
    "codigo_fasciculo",
    "id_no",
    "ordem_sort",
    "num_pontos",
    "estado_bloco",
]
ESTRUTURA_HEADERS_MODEL = ["objectivo", "ambito", "resultado_pretendido_json"]

PONTOS_HEADERS_SUMMARY = [
    "codigo_fasciculo",
    "codigo_bloco",
    "titulo_bloco",
    "point_id",
    "ordem",
    "titulo",
    "estado",
    "llm_freedom",
    "num_premissas",
    "must_include",
    "questoes_abertas",
    "criterios_aceitacao",
]

PONTOS_HEADERS_FULL = [
    "codigo_fasciculo",
    "codigo_bloco",
    "titulo_bloco",
    "point_id",
    "ordem",
    "titulo",
    "estado",
    "llm_freedom",
    "needs_review",
    "template_id",
    "ideia_central",
    "resultado_pretendido",
    "must_include",
    "questoes_abertas",
    "criterios_aceitacao",
    "aceitacao_criterios_lista",
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


def _list_len(lists: dict[str, Any], key: str) -> int:
    val = lists.get(key)
    if isinstance(val, list):
        return len(val)
    return 0


def _walk_estrutura(
    node: StructureTreeNodeSnapshot,
    rows: list[list[Any]],
    *,
    parent_code: str | None,
    fascicle_code: str | None,
    include_block_model: bool,
) -> None:
    if node.node_type == "project":
        for child in node.children:
            _walk_estrutura(
                child,
                rows,
                parent_code=None,
                fascicle_code=None,
                include_block_model=include_block_model,
            )
        return

    fascicle_here = fascicle_code
    if node.node_type == "fascicle":
        fascicle_here = node.display_code or fascicle_code

    production_title = title_with_production_label(
        node.node_type, node.display_code or "", node.title
    )
    num_points = len(node.points) if node.points else 0
    block_status = ""
    if node.node_type == "block" and node.block_status:
        block_status = node.block_status

    row: list[Any] = [
        node.depth,
        node.node_type,
        node.display_code,
        node.title,
        production_title,
        parent_code or "",
        fascicle_here or "",
        node.id,
        node.sort_key,
        num_points,
        block_status,
    ]
    if include_block_model:
        bm = node.block_model
        if bm and node.node_type == "block":
            target_json = (
                json.dumps(bm.target_output, ensure_ascii=False) if bm.target_output else ""
            )
            row.extend([bm.objective.strip(), bm.scope.strip(), target_json])
        else:
            row.extend(["", "", ""])
    rows.append(row)
    child_parent = node.display_code or parent_code
    for child in node.children:
        _walk_estrutura(
            child,
            rows,
            parent_code=child_parent,
            fascicle_code=fascicle_here,
            include_block_model=include_block_model,
        )


def _collect_points(
    node: StructureTreeNodeSnapshot,
    points_rows: list[list[Any]],
    *,
    fascicle_code: str | None,
    block_code: str | None,
    block_title: str | None,
    include_premises: bool,
) -> None:
    fascicle_here = fascicle_code
    if node.node_type == "fascicle":
        fascicle_here = node.display_code or fascicle_code

    code = block_code
    title_blk = block_title
    if node.node_type == "block":
        code = node.display_code or block_code
        title_blk = node.title

    if node.node_type == "block" and node.points:
        for p in node.points:
            if isinstance(p, PointFullSnapshot):
                premises = _premises_text(p.premises) if include_premises and p.premises else ""
                lists = p.lists if isinstance(p.lists, dict) else {}
                points_rows.append(
                    [
                        fascicle_here or "",
                        code or "",
                        title_blk or "",
                        p.id,
                        p.order,
                        p.title,
                        p.status,
                        p.llm_freedom,
                        p.needs_review,
                        p.template_id or "",
                        p.core_idea.strip(),
                        p.intended_outcome.strip(),
                        _list_len(lists, "must_include"),
                        _list_len(lists, "open_questions"),
                        _list_len(lists, "acceptance_criteria"),
                        json.dumps(lists.get("acceptance_criteria") or [], ensure_ascii=False),
                        premises,
                    ]
                )
            else:
                points_rows.append(
                    [
                        fascicle_here or "",
                        code or "",
                        title_blk or "",
                        p.id,
                        p.order,
                        p.title,
                        p.status,
                        p.llm_freedom,
                        p.premise_count,
                        p.must_include_count,
                        p.open_questions_count,
                        p.acceptance_criteria_count,
                    ]
                )

    for child in node.children:
        _collect_points(
            child,
            points_rows,
            fascicle_code=fascicle_here,
            block_code=code,
            block_title=title_blk,
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
        (
            "Folhas",
            "Estrutura: árvore com metadados; Pontos: preparação por bloco (estado, contagens, listas).",
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
        fascicle_code=None,
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
            fascicle_code=None,
            block_code=None,
            block_title=None,
            include_premises=snapshot.options.include_point_premises and full,
        )
        for row_idx, row in enumerate(points_rows, start=2):
            for col_idx, value in enumerate(row, start=1):
                ws_pontos.cell(row=row_idx, column=col_idx, value=value)

    return workbook_to_bytes(wb)