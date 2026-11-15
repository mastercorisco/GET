from __future__ import annotations

SUPPORTED_SCHEMA_VERSION = "1.0.0"
MAX_JSON_BYTES = 5_000_000
MAX_JSON_DEPTH = 50

EDITABLE_FIELDS = frozenset({"title", "content", "rationale", "notes"})