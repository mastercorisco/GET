# get-orient — referência

- Macro M0: `docs/GET_MACRO_PLAN.md`
- Ritual F0 import: `docs/plans/micro-F0-import-ritual.md`
- Fixture mínima: `agent-skills/fixtures/llm-master-snippet.json`
- Exemplos completos: `examples/llm-master-export.example.json`, `examples/get-package-block.example.json`

API útil (leitura):

- `GET /api/knowledge/search?q=…&scope_type=library|project&scope_id=…`
- `GET /api/projects/{id}/summary` — contagens de `status` nos pontos, staging/merges abertos, últimos exports de pacote, `latest_llm_export_id` / `latest_llm_zip_path` (se existir GET-LLM no disco)
- Scripts offline: `macro_pilot_status.py`, `f3_reuse_report.py` (decisões + referências citadas)
- `GET /api/projects/{id}/exports/llm-generation/latest` — ZIP GET-LLM mais recente (manifest + caminhos)
- `GET /api/projects/{id}/imports` (se o utilizador colar JSON de staging — só descrever, não consolidar)

Checklist pré-import F0: `checklist-f0.md` nesta pasta.