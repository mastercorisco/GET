from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[4]


@lru_cache(maxsize=1)
def load_llm_generation_catalog() -> dict[str, Any]:
    path = _REPO_ROOT / "catalogs" / "llm_generation_rules.pt-PT.json"
    if not path.is_file():
        return {
            "generation_rules": {},
            "traceability": {
                "enabled": True,
                "include_knowledge_unit_ids": True,
                "include_requirement_ids": True,
            },
        }
    return json.loads(path.read_text(encoding="utf-8"))