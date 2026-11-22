# Checklist M2 — revisão (get-review)

Após redação em [../get-write-spec/checklist-m2.md](../get-write-spec/checklist-m2.md).

## Entrada

- [ ] `REDACAO-<CODE>.md` final + mesmo ZIP/pacote usado na redação
- [ ] `terminology_{profile}_llm.md` / `.json` do kit ou ZIP

## Comparações (resposta obrigatória)

- [ ] **Registo** — afirmações ↔ premissas, refs, pontos
- [ ] **Decisão** — comportamento ↔ premissas mandatory / decisões citadas
- [ ] **Linguagem** — termos vs glossário e `avoid_in_project`

## Ferramentas

- [ ] `f2_review_report.py` e `f2_glossary_report.py` (ou `f2_m2_gate.py`)
- [ ] PROPOSE apenas como GET-PACKAGE JSON — sem consolidar import

## Fecho M2

- [ ] Inconsistências listadas e priorizadas
- [ ] Actualizar [micro-F2-piloto-EXECUTION-LOG.md](../../docs/plans/micro-F2-piloto-EXECUTION-LOG.md) Definition of Done
- [ ] `t2_readiness_check.py` (MCP continua bloqueado até M2 fechado)