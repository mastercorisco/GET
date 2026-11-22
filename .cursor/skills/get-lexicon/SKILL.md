---
name: get-lexicon
description: Propõe candidatos de glossário via terminology export e GET /api/terminology/search; sem gravar na app.
disable-model-invocation: true
---

# get-lexicon — glossário técnico (READ + PROPOSE)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (tabela get-lexicon). API: ADR-062, `docs/plans/micro-T1-terminology-search.md`.

## Ciclo

**READ → REASON → PROPOSE** (candidatos JSON). **REVIEW / COMMIT** é humano na app ou import posterior — não nesta skill.

## Contexto de leitura

1. No ZIP GET-LLM: `terminology_{profile}_llm.json` (GET-LLM-TERMINOLOGY) e/ou `.md`.
2. API (servidor local `127.0.0.1`):
   - `GET /api/terminology/search?q=…&project_id=<uuid>` — biblioteca + projecto + overrides (`legacy_term`).
   - Sem `project_id`: `scope_type` + `scope_id` como listagem filtrada.
3. Corpus/normas em disco: só material de apoio; não fonte de verdade.
4. Entrada grill/review: termos candidatos sinalizados noutra sessão.

## PROPOSE — formato candidatos

Entregar um objecto JSON (ficheiro ou bloco markdown) **sem** executar POST/PATCH na API, salvo pedido explícito separado do utilizador.

```json
{
  "skill": "get-lexicon",
  "project_id": "uuid-opcional",
  "candidates": [
    {
      "action": "create",
      "scope_type": "library",
      "preferred_term": "…",
      "definition": "…",
      "synonyms": [],
      "avoid_terms": [],
      "notes": "fonte: norma X / corpus Y"
    },
    {
      "action": "override",
      "concept_id": "uuid-existente",
      "legacy_term": "…",
      "usage_note": "…",
      "avoid_in_project": false
    }
  ],
  "conflicts": [
    "termo Z colide com avoid_terms de conceito …"
  ]
}
```

Campos de criação alinhados a `TerminologyCreateRequest`; overrides a `TerminologyOverrideCreateRequest`.

## Regras

- Antes de propor `create`, usar `GET /api/terminology/search` para evitar duplicados.
- Respeitar `avoid_terms` e overrides existentes no projecto.
- Texto redigido fora do GET **não** é fonte de verdade para o léxico.
- Termos de projecto vs biblioteca: preferir biblioteca para reutilização (ADR-012 promoção humana).

## Proibido

- `POST /api/terminology`, `PATCH`, `DELETE` ou overrides **sem** confirmação explícita do utilizador na mesma conversa.
- Acesso directo ao ficheiro SQLite.
- Reimportar glossário MD/JSON do ZIP como verdade canónica.

Ver `reference.md` e `examples.md`.