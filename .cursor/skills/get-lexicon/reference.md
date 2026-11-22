# get-lexicon — referência

- Export pacote: ADR-061 (`terminology_*_llm.md` + `terminology_*_llm.json`)
- Pesquisa: ADR-062 — `GET /api/terminology/search`
- Esquema conceitos: `backend/app/schemas/terminology.py`
- Micro-plano entrega: `docs/plans/micro-get-lexicon-skill.md`

Resposta search (`TerminologySearchHit`):

- `concept` — termo biblioteca ou projecto
- `project_override` — opcional (legado, nota, avoid_in_project)