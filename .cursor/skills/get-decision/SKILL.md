---
name: get-decision
description: Propõe KnowledgeItem decision transversal; não aprovar nem duplicar texto em cada ponto.
disable-model-invocation: true
---

# get-decision — registo de escolha transversal (READ → PROPOSE)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (get-decision). Macro **F3** / reutilização. Perfis tipados `decision/1` — **adiar** até necessidade real ([GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md)).

## Quando usar

- **get-grill** ou **get-review** identificam escolha de engenharia que afecta **mais de um** ponto ou fascículo.
- A decisão não deve ser copiada como parágrafo em cada `DevelopmentPoint`; deve existir **uma vez** na biblioteca/projecto e ser **citada**.

## Modo

- Ciclo: **READ → REASON → PROPOSE** (candidato JSON, não commit).
- Sessão dedicada ou ramo explícito após grill/review.

## Contexto mínimo

1. Descrição da escolha e pontos afectados (`point_id` / códigos documentais).
2. Decisões KI existentes (`GET /api/knowledge/search` ou export).
3. GET-PACKAGE ou excerto do bloco onde surgiu a lacuna.
4. Razão técnica e alternativas rejeitadas (breve).

## PROPOSE — candidato decisão

JSON alinhado a criação de `KnowledgeItem` com `knowledge_type: decision` (e draft coerente com schemas). Incluir:

- `title`, conteúdo da decisão (o que fica fixado).
- `applies_to` / relações sugeridas (pontos ou temas) — como notas se o schema do pacote ainda não tiver ligação tipada.
- Lista **«Pontos que devem referenciar»** (via `knowledge_item_ids` ou `open_questions` fechadas no grill).

Não usar perfil `decision/1` completo até incremento de produto aprovado; preferir decisão como KI com ficha JSON legível.

## Proibido

- Aprovar ou promover para biblioteca sem humano.
- Colar a mesma decisão no `core_idea` de todos os pontos.
- Substituir get-grill/get-review inteiros.
- POST/PATCH na API ou SQLite sem confirmação explícita.
- Inventar UUIDs de KI existentes.

## Handoff

Engenheiro cria/aceita KI na app ou via GET-PACKAGE (F0-knowledge); pontos passam a **referenciar** a decisão, não a duplicá-la.

Ver `reference.md` e `examples.md`.