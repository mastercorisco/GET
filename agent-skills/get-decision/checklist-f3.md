# Checklist F3 — reutilização (get-decision)

Macro: [docs/plans/micro-F3-piloto-EXECUTION-LOG.md](../../docs/plans/micro-F3-piloto-EXECUTION-LOG.md).

## Pré-voo

- [ ] `f3_reuse_report.py --project-id <UUID>` (ou só `f3_decision_citation_report.py`)
- [ ] Identificar decisão duplicada em `core_idea` de vários pontos → candidata a KI `decision`

## Sessão get-decision

- [ ] Uma decisão transversal por PROPOSE (título + conteúdo + pontos que devem referenciar)
- [ ] `knowledge_type: decision`; sem aprovar nem promover biblioteca sem humano
- [ ] Engenheiro cria/aceita KI na app ou GET-PACKAGE (modo knowledge)

## Ligação

- [ ] ≥2 pontos com `knowledge_item_ids` apontando à mesma decisão (grill ou PATCH na UI)
- [ ] Re-correr relatório: `f3_criterion_met` = true para essa decisão

## Validação

- [ ] Export GET-LLM: decisão aparece no pacote de preparação dos pontos
- [ ] **get-review** sem texto contraditório vs KI decisão
- [ ] Actualizar micro-F3-piloto-EXECUTION-LOG e GET_MACRO_PLAN §9 (F3)