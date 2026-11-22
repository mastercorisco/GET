# get-lexicon — reference

- Package export: ADR-061 (`terminology_*_llm.md` + `terminology_*_llm.json`)
- Search: ADR-062 — `GET /api/terminology/search`
- Concept schemas: `backend/app/schemas/terminology.py`
- Delivery micro-plan: `docs/plans/micro-get-lexicon-skill.md`

Search response (`TerminologySearchHit`):

- `concept` — library or project term
- `project_override` — optional (legacy, note, avoid_in_project)