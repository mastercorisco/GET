#!/usr/bin/env python3
"""T2.0 — checklist de arranque MCP (sem iniciar mcp-get/)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_DEFAULT_BASE = "http://127.0.0.1:8000/api"


def _get(url: str) -> tuple[int, dict | list | None]:
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 0, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Pré-voo T2.0 (leitura MCP futura).")
    parser.add_argument("--base-url", default=os.environ.get("GET_API_BASE", _DEFAULT_BASE))
    parser.add_argument("--project-id", help="Validar summary + latest LLM")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    checks: list[dict] = []
    code, _ = _get(f"{base}/health/workspace")
    checks.append({"id": "health_workspace", "ok": code == 200, "http": code})

    if args.project_id:
        code, body = _get(f"{base}/projects/{args.project_id}/summary")
        ok = code == 200 and isinstance(body, dict)
        checks.append({"id": "project_summary", "ok": ok, "http": code})
        if ok and body:
            checks.append(
                {
                    "id": "latest_llm_on_disk",
                    "ok": bool(body.get("latest_llm_zip_path")),
                    "export_id": body.get("latest_llm_export_id"),
                }
            )
        code2, _ = _get(f"{base}/projects/{args.project_id}/exports/llm-generation/latest")
        checks.append({"id": "llm_generation_latest", "ok": code2 == 200, "http": code2})

    manual = [
        {"id": "m2_production", "ok": False, "note": "get-write-spec + get-review + GET-PACKAGE (humano)"},
        {"id": "skills_pilot", "ok": False, "note": "≥2 skills além get-orient/lexicon em sessão real"},
    ]
    auto_ok = all(c.get("ok") for c in checks if "ok" in c)
    payload = {"automated": checks, "manual_pending": manual, "t2_code_allowed": False}

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for c in checks:
            mark = "OK" if c.get("ok") else "—"
            print(f"[{mark}] {c['id']}")
        print("Pendente (humano): M2 produção, pilotos skills.")
        print("mcp-get/: ainda bloqueado até M2 produção fechado (GET_MACRO_PLAN §9).")
    return 0 if auto_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())