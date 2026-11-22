---
name: get-review
description: Cruza texto redigido com GET-LLM e glossário; PROPOSE correcções via GET-PACKAGE, sem novos requisitos.
disable-model-invocation: true
---

# get-review — revisão cruzada (READ → PROPOSE)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (get-review). Conclusão do ciclo **M2**.

## Modo

- Ciclo: **READ → REASON → PROPOSE** (GET-PACKAGE de correcções, não texto livre).
- Entrada: texto de **get-write-spec** + export GET-LLM / pacote bloco actual.

## Contexto mínimo

1. Artefacto MD (ou excerto) da redação.
2. ZIP GET-LLM ou GET-PACKAGE do mesmo âmbito usado na redação.
3. `terminology_{profile}_llm.md` ou search API.
4. Decisões/premissas relevantes no export.

## Três comparações (obrigatórias na resposta)

1. **Registo:** cada afirmação forte ↔ premissa, facto, referência; senão listar como inconsistência ou `open_question` candidata.
2. **Decisão:** comportamento pedido ↔ decisões e premissas `mandatory`.
3. **Linguagem:** termos vs glossário (`avoid_terms`, overrides).

## PROPOSE

- Alterações como **proposta GET-PACKAGE** (JSON completo do envelope; pontos, premissas, refs) — **não** reescrever o caderno inteiro no chat.
- Secção **«Inconsistências»** priorizada.
- **«Não corrigir no GET»** para pureza editorial sem impacto técnico.

## Proibido

- Introduzir requisitos novos não suportados pelos pontos.
- Promover biblioteca; mudar `approved` via pacote.
- Substituir get-write-spec com outra redação completa no chat.
- Consolidar import.

Verificação determinística (opcional): `backend/scripts/f2_review_report.py --draft <md> --block-json <export>`.

Checklist sessão: `checklist-m2-review.md`. Ver `reference.md` e `examples.md`.