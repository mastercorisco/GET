---
name: get-write-spec
description: Author spec caderno text from GET-LLM ZIP; MD artifact outside GET, not reimported as truth.
disable-model-invocation: true
---

# get-write-spec — external authoring (READ → AUTHOR)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-write-spec). Macro F2 / **M2** delivery.

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## Authoring language

The **caderno / spec Markdown** must be written in **Portuguese (pt-PT)** (GET production lexicon).

## Prerequisites

- Target points **`ready`** or **`approved`** (or drafts only if export used `include_draft`).
- Recent **GET-LLM** export (`llm_generation_{profile}.zip`) for project or fascicle. Preflight: `backend/scripts/f2_m2_preflight.py --export`.

## Mode

- Cycle: **READ → AUTHOR** (Markdown or Word in another tool).
- **Not** a PROPOSE-to-SQLite cycle: GET does not treat `.md` as authority.

## Minimal context

1. Unpacked or attached GET-LLM ZIP: `master_*_llm.json`, `manifest.json`, required blocks/fascicles.
2. **`terminology_{profile}_llm.md`** and/or `.json` — binding vocabulary (E05).
3. `generation_rules`, per-point `llm_freedom` (`strict` vs `exploratory`).
4. Explicit scope: block (`display_code`) or fascicle — **not** whole project unless asked.

## Authoring rules

- Honor `must_include`, `limits_and_exclusions`, premises, glossary `avoid_terms` / overrides.
- Structural lexicon (fascículo/capítulo, ponto) from export MD — do not rename technical nodes casually.
- **Exploratory** or unapproved content: mark clearly (e.g. «Sugestões não aprovadas»).
- Do not invent requirements beyond points; gaps → note for **get-review**, not stated as fact.

## Output

- `.md` file (sections aligned to exported block/fascicle) or Word destination.
- Optional: index of covered points ↔ text sections.

## Forbidden

- Change SQLite, use GET-PACKAGE as authoring output instead of MD, or reimport MD into the app.
- Approve content or mark points `ready`/`approved`.
- Ignore technical glossary from ZIP.
- Merge multiple fascicles in one file without explicit request.

## Handoff

Text → **get-review** → fixes via GET-PACKAGE accepted by the engineer.

Session checklist (pt-PT): `checklist-m2.md`. See `reference.md` and `examples.md`.