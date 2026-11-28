"""Workbook GET v1 com folhas 01/02 pré-preenchidas a partir de um catálogo."""

from __future__ import annotations

from openpyxl import Workbook

from app.services.structure_seed.registry import load_catalog
from app.services.workbook.constants import SHEET_BLOCOS, SHEET_FASCICULOS, SHEET_LEITURA
from app.services.workbook.xlsx_writer import (
    write_leitura_sheet,
    write_sheet_headers,
    write_sheet_notes,
    workbook_to_bytes,
)


def build_workbook_structure_from_catalog(catalog_id: str) -> bytes:
    catalog = load_catalog(catalog_id)
    wb = Workbook()
    default = wb.active
    wb.remove(default)

    ws_leitura = wb.create_sheet(SHEET_LEITURA)
    write_leitura_sheet(
        ws_leitura,
        title="GET — Estrutura a partir de catálogo",
        subtitle=f"Catálogo {catalog.id} v{catalog.version}",
    )

    ws_f = wb.create_sheet(SHEET_FASCICULOS)
    write_sheet_notes(ws_f, SHEET_FASCICULOS, "Gerado a partir do catálogo — não altere os cabeçalhos da linha 4.")
    write_sheet_headers(ws_f, SHEET_FASCICULOS)
    row = 5
    for f in catalog.fascicles:
        ws_f.cell(row=row, column=1, value=f.code)
        ws_f.cell(row=row, column=2, value=f.title)
        ws_f.cell(row=row, column=3, value=f.purpose or "Projecto")
        row += 1

    ws_b = wb.create_sheet(SHEET_BLOCOS)
    write_sheet_notes(ws_b, SHEET_BLOCOS, "Gerado a partir do catálogo.")
    write_sheet_headers(ws_b, SHEET_BLOCOS)
    row = 5
    for f in catalog.fascicles:
        for b in f.blocks:
            ws_b.cell(row=row, column=1, value=b.code)
            ws_b.cell(row=row, column=2, value=f.code)
            ws_b.cell(row=row, column=4, value=b.title)
            row += 1

    return workbook_to_bytes(wb)