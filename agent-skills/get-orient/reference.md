# get-orient — reference

- Macro M0: `docs/GET_MACRO_PLAN.md`
- F0 import ritual: `docs/plans/micro-F0-import-ritual.md`
- Minimal fixture: `agent-skills/fixtures/llm-master-snippet.json`
- Full examples: `examples/llm-master-export.example.json`, `examples/get-package-block.example.json`

Cursor skills **do not require** an MCP server until T2.0: exports, scripts, and local API suffice ([GET_MACRO_PLAN.md](../../docs/GET_MACRO_PLAN.md) §9).

Read-only API:

- `GET /api/knowledge/search?q=…&scope_type=library|project&scope_id=…`
- `GET /api/projects/{id}/summary` — point `status` counts, open staging/merges, latest package exports, `latest_llm_export_id` / `latest_llm_zip_path`
- `GET /api/projects/{id}/reuse-report` — F3/M3 citations (decisions + references on points)
- Offline scripts: `macro_pilot_status.py`, `f3_reuse_report.py`
- `GET /api/projects/{id}/exports/llm-generation/latest` — latest GET-LLM ZIP (manifest + paths)
- `GET /api/projects/{id}/imports` (if user pastes staging JSON — describe only, do not consolidate)

F0 pre-import checklist: `checklist-f0.md` in this folder (pt-PT).