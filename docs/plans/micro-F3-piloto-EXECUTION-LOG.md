# F3 — Registo de execução (reutilização)

| Campo | Valor |
|--------|--------|
| Pré-requisito | M2 fechado (recomendado) |
| Estado | **Pendente** |

## Objectivo

Decisão ou premissa mandatória citada em ≥2 contextos sem cópias contraditórias ([GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) § F3).

## Ferramentas

- Skill **get-decision** (`agent-skills/get-decision`)
- Blocos com pontos `ready` + refs no GET

## Piloto

- [ ] Identificar decisão transversal no CTBJ (ex. brownfield / desmontagem)
- [ ] Criar `KnowledgeItem` decision na biblioteca ou projecto
- [ ] Ligar em ≥2 pontos via `knowledge_item_ids` ou premissas
- [ ] Validar com export GET-LLM + get-review

Skill micro: [micro-get-decision-skill.md](micro-get-decision-skill.md).