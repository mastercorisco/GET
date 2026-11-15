from __future__ import annotations

import json


def dumps_deterministic(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))