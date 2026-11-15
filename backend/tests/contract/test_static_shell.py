from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_root_serves_shell_with_assets() -> None:
    client = TestClient(app)
    root = client.get("/")
    assert root.status_code == 200
    body = root.text
    assert 'href="/static/css/tokens.css"' in body
    assert 'src="/static/js/main.js"' in body
    assert "app-nav" in body
    assert 'data-route="workspace"' in body


def test_static_assets_available() -> None:
    client = TestClient(app)
    for path in (
        "/static/css/layout.css",
        "/static/js/router.js",
        "/static/js/labels.js",
        "/static/mockups/shell-mockup-a.html",
    ):
        res = client.get(path)
        assert res.status_code == 200, path