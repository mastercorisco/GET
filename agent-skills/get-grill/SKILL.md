---
name: get-grill
description: Prepare development points via block GET-PACKAGE; PROPOSE editable fields without marking ready.
disable-model-invocation: true
---

# get-grill — prepare block harness (READ → PROPOSE)

Canonical behavior: `docs/GET_SKILLS_PLAN.md` (get-grill). Active pilot: `docs/plans/micro-F1-bloco-F04_B07-grill.md` · prompt: `docs/plans/micro-F1-grill-session-prompt.md`.

## User language

Reply to the engineer in **Portuguese (pt-PT)** unless they request otherwise.

## Mode

- Cycle: **READ → REASON → PROPOSE** (return GET-PACKAGE or valid patch JSON).
- **Grill me:** confirm ideas with the engineer before including them in the proposal.
- Dedicated session: do not mix with get-write-spec or global structural refactor (F0).

## Minimal context

1. GET-PACKAGE exported from the block (`scope_kind: block`) — current canonical JSON from the app.
2. Optional: fascicle/block code (`display_code`), `project_id`.
3. Corpus on disk as support only; final premises/refs go in the proposed package.
4. End a **get-orient** session before opening get-grill on the same block.

## Fields to enrich (editable)

Per point: `title`, `core_idea`, `intended_outcome`, lists (`must_include`, `limits_and_exclusions`, `open_questions`, `acceptance_criteria`, `questions_to_answer`, `development_guidance`, …) per GET-PACKAGE schema.

- `core_idea`: verifiable technical statement (not "write about X").
- `must_include`: concrete obligations, not slogans.
- `open_questions`: honest gaps; if they depend on norm/PDF → flag **get-research**.

Parallel candidates (chat or package section): new `TerminologyConcept`, `Reference` — commit via app/get-lexicon; do not invent protected UUIDs.

## PROPOSE — output

1. Full GET-PACKAGE or clear diff per `point_id`.
2. **Changes per point** section in prose (what changed and why).
3. **For get-research** section if documentary gaps remain.
4. Do **not** include `status: ready` / `approved` on points — human marks in UI after import.

Mentally validate against app rules (`validate_point`): title, core idea, minimum lists before suggesting the engineer mark ready. CLI: `backend/scripts/f1_ready_check.py --block <CODE>`.

## Forbidden

- Set `ready`, `approved`, or protected fields in returned JSON.
- Invent requirements unsupported by export or cited corpus.
- Reorganize whole fascicle or mix knowledge/points/structure in one file (F0 ritual).
- Consolidate import or assume staging accepted.
- Replace human judgment on what enters SQLite.

See `reference.md` and `examples.md`.