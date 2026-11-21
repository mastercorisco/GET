# GET-PACKAGE — SSOT de preenchimento (Onda 2, pós-piloto F0)

**Estado:** Onda 2 implementada (schema + `schema_shapes.py` + `llm_shapes` derivado). Gerador offline opcional para CI permanece roadmap.  
**Decisão:** enriquecer [`schemas/get_package.schema.json`](../../schemas/get_package.schema.json); **gerar** `llm_shapes` a partir da mesma fonte (sem schema separado só para o envelope). Ver **ADR-060**.

## Objectivo

Uma única definição para:

- tipos por lista (`development_guidance` = string; `must_include` = `{text}`; …);
- `enum` de vocabulário fechado (`status`, `llm_freedom`, premissas);
- `required` em todas as chaves de `lists` por ponto;
- exemplos JSON Schema + `sample_from_export` em runtime.

## Componentes

| Camada | Papel |
|--------|--------|
| `get_package.schema.json` | Autoritativo para payload + envelope 1.0.x |
| Gerador (novo módulo) | Lê schema/anotações → `POINT_LIST_SHAPES`, `PACKAGE_ANTI_PATTERNS` |
| `package_guidance.py` | Textos curtos; assertar testes contra gerador |
| `validate_strict` + `package_semantic` | Estrito + avisos F0 |

## Entregáveis Onda 2

1. Script ou módulo `packages/schema_shapes.py` que materializa coleções para `llm_shapes`.
2. Teste contract: export gera `llm_shapes.collections` alinhado ao schema.
3. Bump documentado em ADR + exemplos.

## Fora de âmbito

- Unificar GET-LLM com GET-PACKAGE.
- Validação semântica de conteúdo técnico (só forma + identidade).

## Referências

- Onda 1: identidade DB, `structure_anchor` 1.0.1, relatório conceptual no import.
- [`GET_MACRO_PLAN.md`](../GET_MACRO_PLAN.md) §6.