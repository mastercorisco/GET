from __future__ import annotations

import io
from typing import Any

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.services.workbook.constants import DATA_START_ROW, HEADER_ROW
from app.services.workbook.mapping import SHEET_SPECS


def write_sheet_notes(ws: Worksheet, title: str, subtitle: str, *, hint: str | None = None) -> None:
    ws.cell(row=1, column=1, value=title)
    ws.cell(row=2, column=1, value=subtitle)
    ws.cell(row=3, column=1, value=hint or "Linha 4 = cabeçalhos; dados desde a linha 5.")


def write_sheet_headers(ws: Worksheet, sheet_name: str) -> None:
    spec = SHEET_SPECS[sheet_name]
    for col_idx, column in enumerate(spec.columns, start=1):
        ws.cell(row=HEADER_ROW, column=col_idx, value=column.header)


def write_data_rows(
    ws: Worksheet,
    sheet_name: str,
    rows: list[dict[str, str | None]],
    *,
    start_row: int = DATA_START_ROW,
) -> None:
    spec = SHEET_SPECS[sheet_name]
    for row_idx, row_data in enumerate(rows, start=start_row):
        for col_idx, column in enumerate(spec.columns, start=1):
            value = row_data.get(column.key)
            if value is not None and value != "":
                ws.cell(row=row_idx, column=col_idx, value=value)


def write_leitura_sheet(
    ws: Worksheet,
    *,
    title: str,
    subtitle: str,
    context_rows: list[tuple[str, str]] | None = None,
) -> None:
    write_sheet_notes(ws, title, subtitle)
    ws.cell(row=HEADER_ROW, column=1, value="Finalidade")
    ws.cell(row=HEADER_ROW, column=2, value="Contexto (não importado como entidades).")
    if context_rows:
        for row_idx, (label, value) in enumerate(context_rows, start=DATA_START_ROW):
            ws.cell(row=row_idx, column=1, value=label)
            ws.cell(row=row_idx, column=2, value=value)


def create_data_workbook(sheet_payloads: dict[str, list[dict[str, str | None]]]) -> Workbook:
    """sheet_payloads: sheet name -> data rows (headers must exist on worksheet)."""
    wb = Workbook()
    default = wb.active
    wb.remove(default)
    for sheet_name, rows in sheet_payloads.items():
        if sheet_name not in SHEET_SPECS:
            continue
        ws = wb.create_sheet(sheet_name)
        write_sheet_headers(ws, sheet_name)
        if rows:
            write_data_rows(ws, sheet_name, rows)
    return wb


def workbook_to_bytes(wb: Workbook) -> bytes:
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()