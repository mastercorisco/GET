---
name: get-orient
description: Read-only GET orientation from GET-LLM/GET-PACKAGE exports and API search; no import proposals.
disable-model-invocation: true
---

# get-orient — situation briefing (READ-ONLY)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-orient). Pilot plan: `docs/plans/micro-get-orient-skill.md`.

**F0 pre-import checklist:** `checklist-f0.md` in this folder — use when the next session is F0-structure/content/knowledge ritual (not a substitute for get-grill).

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## Mode

- Cycle: **READ → REASON → ANSWER** (not PROPOSE by default).
- Explicit session: the user asked for orientation, not grill or authoring.

## Minimal context

1. Active GET workspace path (`GET_WORKSPACE_ROOT` or `~/.get/app-config.json`).
2. At least one of:
   - `exports/EXP-LLM-…/manifest.json` + `master_{profile}_llm.json` (panorama), or
   - GET-PACKAGE folder fascicle/block (`PKG-FASC-…`, `PKG-BLK-…`).
3. Optional: `GET /api/knowledge/search?q=…&scope_type=library` (server on `127.0.0.1`).
4. Verbal confirmation: orientation only, no import JSON.

## Ritual

1. Confirm get-orient mode.
2. Limit answers to provided context; if data is missing, say "not in the provided context".
3. Reply using the fixed sections (template below).
4. If editing work appears → close and suggest a new **get-grill** session with a fresh GET-PACKAGE.

## Output template

```markdown
## State
(factual summary from export/search)

## Gaps
(missing harness, refs, glossary, staging)

## Import risks
(structure/content mix, volume, conceptual_warnings if any)

## Suggested next step
(one following skill: F0 ritual, get-grill block X, new export, etc.)
```

## Forbidden

- Return GET-PACKAGE or import JSON as the default answer.
- Set `ready`, `approved`, or change protected fields.
- Invent counts, UUIDs, or facts not in export/search.
- Replace FTS/knowledge search for claims that need exact KI citations.

## Depth by artifact

| Level | Artifact |
|-------|----------|
| Panorama | GET-LLM master + manifest |
| Fascicle | GET-LLM fascicle index or GET-PACKAGE fascicle |
| Block | GET-PACKAGE block |
| Library | Knowledge search or KI in master |

See also `reference.md` and `examples.md` in this folder.