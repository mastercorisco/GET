---
name: get-decision
description: Propose cross-cutting KnowledgeItem decision; do not approve or duplicate text in every point.
disable-model-invocation: true
---

# get-decision — cross-cutting choice (READ → PROPOSE)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-decision). Macro **F3** / reuse. Typed profile `decision/1` — **defer** until needed ([GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md)).

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## When to use

- **get-grill** or **get-review** surface an engineering choice affecting **more than one** point or fascicle.
- The decision must not be copied as a paragraph in each `DevelopmentPoint`; exist **once** in library/project and be **cited**.

## Mode

- Cycle: **READ → REASON → PROPOSE** (candidate JSON, no commit).
- Dedicated session or explicit branch after grill/review.

## Minimal context

1. Choice description and affected points (`point_id` / document codes).
2. Existing decision KIs (`GET /api/knowledge/search` or export).
3. GET-PACKAGE or block excerpt where the gap appeared.
4. Technical rationale and rejected alternatives (brief).

## PROPOSE — decision candidate

JSON aligned to `KnowledgeItem` creation with `knowledge_type: decision`. Include:

- `title`, decision content (what is fixed).
- Suggested `applies_to` / relations — as notes if package schema lacks typed links.
- **Points that should reference** (via `knowledge_item_ids` or grill-closed `open_questions`).

Do not use full `decision/1` profile until product increment approved; prefer decision as readable KI JSON.

## Forbidden

- Approve or promote to library without human.
- Paste the same decision into every point `core_idea`.
- Replace entire get-grill/get-review sessions.
- POST/PATCH API or SQLite without explicit confirmation.
- Invent existing KI UUIDs.

## Handoff

Engineer creates/accepts KI in app or via GET-PACKAGE (F0-knowledge); points **reference** the decision, not duplicate it.

Session checklist (pt-PT): `checklist-f3.md`. Report: `backend/scripts/f3_decision_citation_report.py`. See `reference.md` and `examples.md`.