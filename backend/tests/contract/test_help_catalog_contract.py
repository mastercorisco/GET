from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_PATH = REPO_ROOT / "catalogs" / "get_help_catalog.pt-PT.json"
SHELL_HTML = REPO_ROOT / "backend" / "app" / "static" / "index.html"

HELP_KEY_RE = re.compile(r'data-help-key="([^"]+)"')


def _load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def test_help_catalog_field_schema() -> None:
    catalog = _load_catalog()
    fields = catalog.get("fields") or {}
    assert fields, "fields vazio"
    for key, entry in fields.items():
        assert isinstance(entry, dict), key
        for required in ("label", "short_help", "definition"):
            assert entry.get(required), f"{key} falta {required}"


def test_shell_help_keys_in_catalog() -> None:
    catalog = _load_catalog()
    fields = catalog.get("fields") or {}
    html = SHELL_HTML.read_text(encoding="utf-8")
    keys = sorted(set(HELP_KEY_RE.findall(html)))
    missing = [k for k in keys if k not in fields]
    assert not missing, "Chaves HTML sem entrada no catálogo: " + ", ".join(missing)


def test_api_catalog_help_includes_screens() -> None:
    client = TestClient(app)
    res = client.get("/api/catalogs/help")
    assert res.status_code == 200
    data = res.json()
    assert data.get("catalog_version")
    screens = data.get("screens") or {}
    assert "block-editor" in screens
    assert screens["block-editor"].get("title")