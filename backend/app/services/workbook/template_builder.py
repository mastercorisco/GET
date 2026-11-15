from __future__ import annotations

import io

from openpyxl import Workbook

from app.services.workbook.constants import (
    DATA_SHEETS,
    HEADER_ROW,
    SHEET_A01,
    SHEET_ARTEFACTOS,
    SHEET_BLOCOS,
    SHEET_FASCICULOS,
    SHEET_FILOSOFIA,
    SHEET_LEITURA,
    SHEET_MAPA,
)
from app.services.workbook.mapping import SHEET_SPECS

TEMPLATE_IDS = {
    "library_import_v1": "Biblioteca — modelo GET v1",
    "project_import_v1": "Projecto — modelo GET v1",
}


def _write_notes(ws, title: str, subtitle: str) -> None:
    ws.cell(row=1, column=1, value=title)
    ws.cell(row=2, column=1, value=subtitle)
    ws.cell(row=3, column=1, value="Linha 4 = cabeçalhos; dados desde a linha 5.")


def _write_headers(ws, sheet_name: str) -> None:
    spec = SHEET_SPECS[sheet_name]
    for col_idx, column in enumerate(spec.columns, start=1):
        ws.cell(row=HEADER_ROW, column=col_idx, value=column.header)


def build_workbook_template(template_id: str) -> bytes:
    if template_id not in TEMPLATE_IDS:
        raise ValueError(f"Template desconhecido: {template_id}")

    wb = Workbook()
    default = wb.active
    wb.remove(default)

    ws_leitura = wb.create_sheet(SHEET_LEITURA)
    _write_notes(
        ws_leitura,
        "GET — Modelo de importação v1",
        TEMPLATE_IDS[template_id],
    )
    ws_leitura.cell(row=HEADER_ROW, column=1, value="Finalidade")
    ws_leitura.cell(
        row=HEADER_ROW,
        column=2,
        value="Preencher contexto narrativo do projecto (não importado para a BD).",
    )

    for sheet_name in DATA_SHEETS:
        ws = wb.create_sheet(sheet_name)
        _write_notes(ws, sheet_name, "Modelo controlado GET — não altere os cabeçalhos da linha 4.")
        _write_headers(ws, sheet_name)

        if sheet_name == SHEET_FASCICULOS:
            ws.cell(row=5, column=1, value="F01")
            ws.cell(row=5, column=2, value="Exemplo de fascículo")
            ws.cell(row=5, column=3, value="Projeto / parcialmente reutilizável")
        if sheet_name == SHEET_BLOCOS and template_id == "project_import_v1":
            ws.cell(row=5, column=1, value="F01_B01")
            ws.cell(row=5, column=2, value="F01")
            ws.cell(row=5, column=4, value="Exemplo de bloco")
        if sheet_name == SHEET_FILOSOFIA:
            ws.cell(row=5, column=1, value="P-001")
            ws.cell(row=5, column=2, value="Princípio exemplo")
            ws.cell(row=5, column=3, value="Definição exemplo")
        if sheet_name == SHEET_ARTEFACTOS:
            ws.cell(row=5, column=1, value="A-001")
            ws.cell(row=5, column=2, value="Artefacto exemplo")
        if sheet_name == SHEET_A01:
            ws.cell(row=5, column=1, value="FN-001")
            ws.cell(row=5, column=2, value="Sistema exemplo")
            ws.cell(row=5, column=3, value="Função exemplo")
        if sheet_name == SHEET_MAPA:
            ws.cell(row=5, column=1, value="EN 61131-3")
            ws.cell(row=5, column=2, value="Referência informativa")

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def template_filename(template_id: str) -> str:
    return f"{template_id}.xlsx"