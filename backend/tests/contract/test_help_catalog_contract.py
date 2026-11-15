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
GENERIC_PURPOSE = re.compile(r"^No GET, este campo «")


def _load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def test_help_catalog_field_schema() -> None:
    catalog = _load_catalog()
    fields = catalog.get("fields") or {}
    assert fields, "fields vazio"
    assert catalog.get("catalog_version") == "1.3.1"
    for key, entry in fields.items():
        assert isinstance(entry, dict), key
        for required in ("label", "short_help", "definition"):
            assert entry.get(required), f"{key} falta {required}"


def test_help_catalog_method_block() -> None:
    catalog = _load_catalog()
    method = catalog.get("method") or {}
    assert method.get("principle")
    assert method.get("governance_rules")
    sem = method.get("exchange_semantics") or {}
    for key in ("authoritative_content", "supporting_context", "unresolved_matters", "generation_instructions"):
        assert sem.get(key), key


def test_shell_help_keys_v12_user_oriented() -> None:
    """Chaves data-help-key no HTML: contexto GET."""
    catalog = _load_catalog()
    fields = catalog.get("fields") or {}
    concepts = catalog.get("concepts") or {}
    html = SHELL_HTML.read_text(encoding="utf-8")
    keys = sorted(set(HELP_KEY_RE.findall(html)))
    missing_ctx: list[str] = []
    bad_concepts: list[str] = []
    for key in keys:
        entry = fields.get(key) or {}
        if not entry.get("purpose_in_app") or not entry.get("workflow_context"):
            missing_ctx.append(key)
        for cid in entry.get("related_concepts") or []:
            if cid not in concepts:
                bad_concepts.append(f"{key} -> {cid}")
    assert not missing_ctx, "Sem purpose_in_app/workflow_context: " + ", ".join(missing_ctx)
    assert not bad_concepts, "related_concepts inválidos: " + ", ".join(bad_concepts)


def test_concepts_v13_shape() -> None:
    catalog = _load_catalog()
    concepts = catalog.get("concepts") or {}
    assert concepts
    for cid, c in concepts.items():
        assert c.get("summary"), cid
        assert c.get("role_in_get"), cid
        assert c.get("not_this"), cid


def test_development_point_fields_not_generic() -> None:
    catalog = _load_catalog()
    fields = catalog.get("fields") or {}
    bad: list[str] = []
    for key, entry in fields.items():
        if not key.startswith("development_point."):
            continue
        purpose = entry.get("purpose_in_app") or ""
        if GENERIC_PURPOSE.match(purpose):
            bad.append(key)
    assert not bad, "development_point com purpose genérico: " + ", ".join(bad)


def test_fields_have_purpose_in_app() -> None:
    catalog = _load_catalog()
    fields = catalog.get("fields") or {}
    missing = [k for k, e in fields.items() if not (e.get("purpose_in_app") or "").strip()]
    assert not missing, "Campos sem purpose_in_app: " + ", ".join(missing[:10])


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
    assert data.get("catalog_version") == "1.3.1"
    assert data.get("method", {}).get("principle")
    screens = data.get("screens") or {}
    assert "block-editor" in screens
    assert screens["block-editor"].get("title")