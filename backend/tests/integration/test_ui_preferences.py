from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.deps import get_settings
from app.main import app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    cfg = tmp_path / "app-config.json"
    prefs = tmp_path / "ui-preferences.json"
    monkeypatch.setenv("GET_APP_CONFIG_PATH", str(cfg))
    monkeypatch.setenv("GET_UI_PREFERENCES_PATH", str(prefs))
    get_settings.cache_clear()
    return TestClient(app)


def test_ui_preferences_defaults(client: TestClient) -> None:
    res = client.get("/api/ui-preferences")
    assert res.status_code == 200
    data = res.json()
    assert data["theme"] == "light"
    assert data["density"] == "normal"
    assert data["schema_version"] == "1.1"


def test_ui_preferences_patch_roundtrip(client: TestClient) -> None:
    res = client.patch(
        "/api/ui-preferences",
        json={"theme": "dark", "density": "compact", "accent": "teal"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["theme"] == "dark"
    assert data["density"] == "compact"
    assert data["accent"] == "teal"
    res2 = client.get("/api/ui-preferences")
    assert res2.json() == data


def test_ui_preferences_reset(client: TestClient) -> None:
    client.patch("/api/ui-preferences", json={"theme": "dark"})
    res = client.patch("/api/ui-preferences", json={"reset_defaults": True})
    assert res.json()["theme"] == "light"


def test_ui_preferences_invalid_enum(client: TestClient) -> None:
    res = client.patch("/api/ui-preferences", json={"theme": "neon"})
    assert res.status_code == 422


def test_ui_preferences_custom_accent_color(client: TestClient) -> None:
    res = client.patch(
        "/api/ui-preferences",
        json={"accent": "custom", "accent_color": "#7c3aed", "density": "custom", "textarea_min_height_rem": 4.5},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["accent"] == "custom"
    assert data["accent_color"] == "#7c3aed"
    assert data["textarea_min_height_rem"] == 4.5