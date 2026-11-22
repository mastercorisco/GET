# Checklist M2 — redação (get-write-spec)

Complemento macro: [docs/plans/micro-F2-M2-production-checklist.md](../../docs/plans/micro-F2-M2-production-checklist.md).

## Pré-voo (GET)

- [ ] Bloco com pontos `ready`/`approved` — `f1_ready_check.py --block <CODE>`
- [ ] GET-LLM recente — `f2_m2_preflight.py --export` ou API `exports/llm-generation/latest`
- [ ] Kit no workspace — `f2_m2_workflow.py --draft-from-export` (materialize + dry-run opcional)

## Sessão write-spec

- [ ] Âmbito = um bloco (ou fascículo) por ficheiro MD
- [ ] `must_include`, `limits_and_exclusions`, premissas e glossário do ZIP respeitados
- [ ] Sem marcar pontos `ready`/`approved` nem alterar SQLite
- [ ] Lacunas explícitas para **get-review**, não preenchidas como facto

## Artefacto

- [ ] `redaction/<CODE>/REDACAO-<CODE>.md` (redação final, não só draft script)
- [ ] Gate tooling: `f2_m2_gate.py` no MD final (must_include + glossário)
- [ ] Estado repo: `f2_m2_production_status.py --project-id <UUID> --block <CODE>`

## Handoff

- [ ] Prompt [micro-F2-review-session](../../docs/plans/micro-F2-review-session-F04_B07.md) (adaptar CODE)
- [ ] Correcções só via GET-PACKAGE aceite na UI — **não** reimportar MD