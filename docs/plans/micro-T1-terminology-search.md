# Micro-plano — pesquisa de glossário (T1)

**Macro:** [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) §3.2 onda T1, §6 backlog.  
**Precede:** glossário no ZIP GET-LLM (T0, ADR-061).

## Objectivo

`GET /api/terminology/search` para skills (get-lexicon, get-orient) e MCP futuro consultarem vocabulário sem descarregar o ZIP inteiro.

## Fora de âmbito

- FTS SQLite dedicado; MCP; skill Cursor get-lexicon versionada (só documentação).
- Escritas ou staging de propostas.

## Contrato

| Parâmetro | Obrigatório | Uso |
|-----------|-------------|-----|
| `q` | sim | Tokens alfanuméricos; todos devem aparecer (AND) em algum campo pesquisável. |
| `project_id` | não | Se presente: biblioteca + termos do projecto; inclui `legacy_term` / `usage_note` dos overrides. |
| `scope_type`, `scope_id` | se sem `project_id` | Igual a `GET /api/terminology` (biblioteca ou projecto isolado). |

## Campos pesquisáveis

`preferred_term`, `definition`, `acronym`, `synonyms`, `avoid_terms`, `domain`, `notes`, `technical_translation`; com `project_id`, também override `legacy_term` e `usage_note`.

## Resposta

Lista de `TerminologySearchHit`: `concept` + `project_override` opcional.

## Critérios de aceitação

- [x] Endpoint registado antes de `/terminology/{concept_id}`.
- [x] Pesquisa por sinónimo na biblioteca.
- [x] Pesquisa com `project_id` cruza override legado.
- [x] Consulta vazia → HTTP 400.
- [x] Testes em `test_e05_terminology.py`.
- [x] ADR-062 e macro plan actualizados.

## Verificação manual

1. Criar termo com sinónimo na biblioteca.
2. `GET /api/terminology/search?q=<sinónimo>`.
3. Com projecto e override: `GET /api/terminology/search?q=<legado>&project_id=…`.