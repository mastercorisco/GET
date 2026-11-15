from __future__ import annotations

import json
import uuid
from pathlib import Path

from app.services.imports.constants import MAX_JSON_BYTES, MAX_JSON_DEPTH


class IngestError(Exception):
    pass


def _depth(value: object, current: int = 0) -> int:
    if current > MAX_JSON_DEPTH:
        return current
    if isinstance(value, dict):
        if not value:
            return current + 1
        return max(_depth(v, current + 1) for v in value.values())
    if isinstance(value, list):
        if not value:
            return current + 1
        return max(_depth(v, current + 1) for v in value)
    return current + 1


def parse_upload_bytes(raw: bytes) -> dict:
    if not raw:
        raise IngestError("Ficheiro vazio ou JSON truncado.")
    if len(raw) > MAX_JSON_BYTES:
        raise IngestError("Ficheiro excede o tamanho máximo permitido.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestError("Ficheiro não é UTF-8 válido.") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IngestError("JSON inválido ou truncado.") from exc
    if not isinstance(data, dict):
        raise IngestError("O pacote deve ser um objecto JSON.")
    if _depth(data) > MAX_JSON_DEPTH:
        raise IngestError("JSON excede a profundidade máxima.")
    return data


def write_import_file(imports_dir: Path, import_id: str, filename: str, raw: bytes) -> Path:
    folder = imports_dir / import_id
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / filename
    dest.write_bytes(raw)
    return dest


def new_import_id() -> str:
    return str(uuid.uuid4())