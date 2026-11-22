from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

PKG_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PKG_ROOT.parent
MANIFEST_PATH = PKG_ROOT / "MANIFEST.json"
CURSOR_SKILLS = REPO_ROOT / ".cursor" / "skills"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        pytest.fail("SKILL.md sem frontmatter YAML")
    block = match.group(1)
    result: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value in {">-", ">", "|"}:
            continue
        if key:
            result[key] = value
    return result


def _skill_md(skill: str) -> str:
    path = PKG_ROOT / skill / "SKILL.md"
    assert path.is_file(), f"Missing {path}"
    return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def manifest() -> dict:
    return _load_manifest()


@pytest.mark.parametrize("skill", _load_manifest()["skills"])
def test_manifest_skill_dir_exists(skill: str) -> None:
    assert (PKG_ROOT / skill / "SKILL.md").is_file()


@pytest.mark.parametrize("skill", _load_manifest()["skills"])
def test_skill_frontmatter(skill: str) -> None:
    text = _skill_md(skill)
    meta = _parse_frontmatter(text)
    assert meta.get("name") == skill
    assert meta.get("description") and len(meta["description"]) >= 10


REQUIRED_SECTIONS: dict[str, list[str]] = {
    "get-orient": [
        "READ-ONLY",
        "Contexto mínimo",
        "Proibido",
    ],
    "get-lexicon": [
        "GET /api/terminology/search",
        "Proibido",
        "Ciclo",
    ],
    "get-grill": [
        "GET-PACKAGE",
        "Proibido",
        "Contexto mínimo",
    ],
    "get-research": [
        "Proibido",
        "Contexto mínimo",
        "PROPOSE",
    ],
    "get-write-spec": [
        "GET-LLM",
        "terminology",
        "Proibido",
        "Contexto mínimo",
    ],
    "get-review": [
        "PROPOSE",
        "Proibido",
        "GET-PACKAGE",
    ],
}


@pytest.mark.parametrize("skill,sections", list(REQUIRED_SECTIONS.items()))
def test_required_sections(skill: str, sections: list[str]) -> None:
    text = _skill_md(skill)
    for section in sections:
        assert section in text, f"{skill}: missing '{section}'"


@pytest.mark.parametrize("skill", _load_manifest()["skills"])
def test_cursor_sync_byte_identical(skill: str) -> None:
    src = PKG_ROOT / skill / "SKILL.md"
    dest = CURSOR_SKILLS / skill / "SKILL.md"
    if not dest.is_file():
        pytest.skip("Run sync-to-cursor before asserting .cursor/skills")
    assert src.read_bytes() == dest.read_bytes(), f"Drift: run sync for {skill}"