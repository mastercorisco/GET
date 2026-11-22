---
name: get-lexicon
description: Propose glossary candidates from terminology export and GET /api/terminology/search; no writes to the app.
disable-model-invocation: true
---

# get-lexicon — technical glossary (READ + PROPOSE)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-lexicon table). API: ADR-062, `docs/plans/micro-T1-terminology-search.md`.

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## Cycle

**READ → REASON → PROPOSE** (candidate JSON). **REVIEW / COMMIT** is human in the app or later import — not in this skill.

## Minimal context

1. In GET-LLM ZIP: `terminology_{profile}_llm.json` (GET-LLM-TERMINOLOGY) and/or `.md`.
2. API (local server `127.0.0.1`):
   - `GET /api/terminology/search?q=…&project_id=<uuid>` — library + project + overrides (`legacy_term`).
   - Without `project_id`: use `scope_type` + `scope_id` as filtered listing.
3. Corpus/norms on disk: support material only; not source of truth.
4. Grill/review input: candidate terms flagged in another session.

## PROPOSE — candidate format

Deliver a JSON object (file or markdown block) **without** POST/PATCH on the API unless the user explicitly asks in a separate step.

```json
{
  "skill": "get-lexicon",
  "project_id": "optional-uuid",
  "candidates": [
    {
      "action": "create",
      "scope_type": "library",
      "preferred_term": "…",
      "definition": "…",
      "synonyms": [],
      "avoid_terms": [],
      "notes": "source: norm X / corpus Y"
    },
    {
      "action": "override",
      "concept_id": "existing-uuid",
      "legacy_term": "…",
      "usage_note": "…",
      "avoid_in_project": false
    }
  ],
  "conflicts": [
    "term Z collides with avoid_terms on concept …"
  ]
}
```

Create fields align with `TerminologyCreateRequest`; overrides with `TerminologyOverrideCreateRequest`.

## Rules

- Before `create`, use `GET /api/terminology/search` to avoid duplicates.
- Respect existing `avoid_terms` and project overrides.
- External authored text is **not** glossary source of truth.
- Project vs library terms: prefer library for reuse (ADR-012 human promotion).

## Forbidden

- `POST /api/terminology`, `PATCH`, `DELETE`, or overrides **without** explicit user confirmation in the same conversation.
- Direct SQLite file access.
- Reimport glossary MD/JSON from ZIP as canonical truth.

See `reference.md` and `examples.md`.