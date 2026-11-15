from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.services.workbook.constants import DATA_START_ROW, HEADER_ROW


def normalize_cell(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    text = str(value).strip()
    return text or None


def row_is_empty(values: tuple[Any, ...]) -> bool:
    return all(normalize_cell(v) is None for v in values)


class WorkbookReader:
    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        self._wb = load_workbook(self.path, read_only=True, data_only=True)

    def sheet_names(self) -> list[str]:
        return list(self._wb.sheetnames)

    def header_row(self, sheet_name: str) -> list[str | None]:
        ws = self._sheet(sheet_name)
        row = next(ws.iter_rows(min_row=HEADER_ROW, max_row=HEADER_ROW, values_only=True), ())
        return [normalize_cell(c) for c in row]

    def iter_data_rows(self, sheet_name: str) -> Iterator[tuple[int, tuple[Any, ...]]]:
        ws = self._sheet(sheet_name)
        for index, row in enumerate(
            ws.iter_rows(min_row=DATA_START_ROW, values_only=True),
            start=DATA_START_ROW,
        ):
            if row_is_empty(row):
                continue
            yield index, row

    def cell_text(self, sheet_name: str, row: int, col: int) -> str | None:
        ws = self._sheet(sheet_name)
        values = next(ws.iter_rows(min_row=row, max_row=row, values_only=True), ())
        if col - 1 >= len(values):
            return None
        return normalize_cell(values[col - 1])

    def _sheet(self, sheet_name: str) -> Worksheet:
        if sheet_name not in self._wb.sheetnames:
            raise KeyError(f"Folha em falta: {sheet_name}")
        return self._wb[sheet_name]

    def close(self) -> None:
        self._wb.close()