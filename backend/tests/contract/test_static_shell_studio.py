from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SHELL = REPO_ROOT / "backend" / "app" / "static" / "index.html"


def test_shell_links_studio_css() -> None:
    html = SHELL.read_text(encoding="utf-8")
    assert "/static/css/studio.css" in html
    assert 'data-route="library"' in html
    assert "route-tab-bar" in html