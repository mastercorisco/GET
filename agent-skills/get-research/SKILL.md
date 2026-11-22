---
name: get-research
description: Support get-grill with norms and corpus; propose Reference and facts without marking verified in the app.
disable-model-invocation: true
---

# get-research — focused documentary support (READ → PROPOSE)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-research). Coupled to **get-grill**, does not replace it.

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## Mode

- Cycle: **READ → REASON → PROPOSE** (reference / fact / corpus summary proposals).
- **One gap per session** — do not research the whole block.
- Triggered by grill `open_questions`, unverified premise, or `must_include` needing clause/datasheet.

## Minimal context

1. Concrete gap (grill text or `point_id`).
2. Block GET-PACKAGE or relevant excerpt.
3. Corpus on disk (`corpus/…`) or URLs from the engineer.
4. Existing GET refs (`GET /api/references`, KI in export) — avoid duplicates.

## PROPOSE — allowed outputs

| Type | Content |
|------|---------|
| **Reference** | `citation`, `notes`, `internal_location` (local path or SharePoint) |
| **Corpus summary** | Derived MD on disk (not reimportable as truth) |
| **Fact** (optional) | Candidate KI that **cites** the ref — for GET-PACKAGE F0-knowledge or later import |

Deliver JSON aligned to app schemas or clear sections for the engineer to paste into GET-PACKAGE.

## Forbidden

- Mark premise or reference **verified** without human decision.
- Convert a whole norm into block requirements without grill.
- Generic search across all fascicle points.
- POST to API / direct SQLite without explicit confirmation.
- Use external authored text as source of truth.

## Handoff

Return to **get-grill** flow or F0-knowledge import; consolidate always human in the app.

Reuse checklist (pt-PT): `checklist-m3-references.md`. Report: `f3_reference_citation_report.py`. See `reference.md` and `examples.md`.