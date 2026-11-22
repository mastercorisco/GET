# F1 — Bloco piloto (get-grill) — esboço

**Pré-requisito:** F0 fechada ([micro-F0-retro-TEMPLATE.md](micro-F0-retro-TEMPLATE.md) preenchido).

## Objectivo

Um bloco no fascículo estabilizado em F0 com pontos **harness** completos; caminho até `ready` (marcação **humana** na UI).

## Escopo

| Incluído | Excluído |
|----------|----------|
| **get-orient** (ponto de situação) → sessões get-grill + get-research pontual | get-write-spec (→ F2) |
| Propostas GET-PACKAGE (campos ponto, refs) | decision/1, MCP |
| `Reference` com URL SharePoint ou caminho em `citation`/`notes` | Marcar `approved` via import |

## Passos (a detalhar após F0)

1. Escolher bloco (código documental + tema técnico adequado para grill).
2. Export GET-PACKAGE `scope.kind=block`.
3. Modo grill me: confirmar ideias antes de propor listas.
4. Aceitar propostas → validação app → marcar `ready` manualmente ponto a ponto.
5. Critérios: [GET_SKILLS_PLAN.md](../GET_SKILLS_PLAN.md) + `validate_point` na app.

## Entrega M1

≥1 bloco com todos os pontos alvo em `ready`, sem alertas de validação bloqueantes.

Ver [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) F1.