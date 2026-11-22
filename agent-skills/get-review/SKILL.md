---
name: get-review
description: Cross-check authored text vs GET-LLM and glossary; PROPOSE fixes via GET-PACKAGE, no new requirements.
disable-model-invocation: true
---

# get-review — cross-check (READ → PROPOSE)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-review). Closes the **M2** cycle.

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## Mode

- Cycle: **READ → REASON → PROPOSE** (correction GET-PACKAGE, not free-form rewrite).
- Input: **get-write-spec** text + current GET-LLM / block package.

## Minimal context

1. MD artifact (or excerpt) from authoring.
2. GET-LLM ZIP or GET-PACKAGE for the same scope used in authoring.
3. `terminology_{profile}_llm.md` or search API.
4. Relevant decisions/premises in export.

## Three comparisons (required in response)

1. **Record:** each strong claim ↔ premise, fact, reference; else list inconsistency or candidate `open_question`.
2. **Decision:** requested behavior ↔ decisions and `mandatory` premises.
3. **Language:** terms vs glossary (`avoid_terms`, overrides).

## PROPOSE

- Changes as **GET-PACKAGE proposal** (full envelope JSON; points, premises, refs) — **do not** rewrite the whole caderno in chat.
- Prioritized **Inconsistencies** section.
- **Do not fix in GET** for editorial-only issues with no technical impact.

## Forbidden

- Introduce new requirements unsupported by points.
- Promote to library; change `approved` via package.
- Replace get-write-spec with another full draft in chat.
- Consolidate import.

Optional deterministic check: `backend/scripts/f2_review_report.py --draft <md> --block-json <export>`.

Session checklist (pt-PT): `checklist-m2-review.md`. See `reference.md` and `examples.md`.