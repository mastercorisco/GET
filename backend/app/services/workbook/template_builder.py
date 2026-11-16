from __future__ import annotations

from openpyxl import Workbook

from app.services.workbook.constants import (
    DATA_SHEETS,
    SHEET_A01,
    SHEET_ARTEFACTOS,
    SHEET_BLOCOS,
    SHEET_FASCICULOS,
    SHEET_FILOSOFIA,
    SHEET_LEITURA,
    SHEET_MAPA,
)
from app.services.workbook.xlsx_writer import (
    write_leitura_sheet,
    write_sheet_headers,
    write_sheet_notes,
    workbook_to_bytes,
)

TEMPLATE_IDS = {
    "library_import_v1": "Biblioteca — modelo GET v1",
    "project_import_v1": "Projecto — modelo GET v1",
}


def build_workbook_template(template_id: str) -> bytes:
    if template_id not in TEMPLATE_IDS:
        raise ValueError(f"Template desconhecido: {template_id}")

    wb = Workbook()
    default = wb.active
    wb.remove(default)

    ws_leitura = wb.create_sheet(SHEET_LEITURA)
    write_leitura_sheet(
        ws_leitura,
        title="GET — Modelo de importação v1",
        subtitle=TEMPLATE_IDS[template_id],
    )

    for sheet_name in DATA_SHEETS:
        ws = wb.create_sheet(sheet_name)
        write_sheet_notes(ws, sheet_name, "Modelo controlado GET — não altere os cabeçalhos da linha 4.")
        write_sheet_headers(ws, sheet_name)

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

    return workbook_to_bytes(wb)


def template_filename(template_id: str) -> str:
    return f"{template_id}.xlsx"