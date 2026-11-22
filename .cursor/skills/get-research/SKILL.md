---
name: get-research
description: Apoia get-grill com normas e corpus; propõe Reference e factos, sem marcar verificado na app.
disable-model-invocation: true
---

# get-research — apoio documental pontual (READ → PROPOSE)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (get-research). Acoplado a **get-grill**, não substitui.

## Modo

- Ciclo: **READ → REASON → PROPOSE** (propostas de referência / facto / resumo corpus).
- **Uma lacuna por sessão** — não pesquisar “todo o bloco”.
- Disparado por `open_questions` do grill, premissa `unverified`, ou `must_include` que exige cláusula/datasheet.

## Contexto mínimo

1. Lacuna concreta (texto do grill ou ponto `point_id`).
2. GET-PACKAGE do bloco ou excerto relevante.
3. Corpus em disco (`corpus/…`) ou URLs indicadas pelo engenheiro.
4. Refs GET existentes (`GET /api/references`, KI no export) — evitar duplicar.

## PROPOSE — saídas permitidas

| Tipo | Conteúdo |
|------|----------|
| **Reference** | `citation`, `notes`, `internal_location` (caminho local ou SharePoint) |
| **Resumo corpus** | MD derivado no disco (não reimportável como verdade) |
| **Fact** (opcional) | KI candidato que **cita** a ref — para GET-PACKAGE F0-knowledge ou import posterior |

Entregar JSON alinhado a schemas da app ou secções claras para o engenheiro colar no GET-PACKAGE.

## Proibido

- Marcar premissa ou referência como **verificada** sem decisão humana.
- Converter norma inteira em requisitos no pacote do bloco sem grill.
- Pesquisa genérica em todos os pontos do fascículo.
- POST na API / SQLite directo sem confirmação explícita.
- Usar texto redigido externo como fonte de verdade.

## Handoff

Devolver resultado ao fluxo **get-grill** ou import F0-knowledge; consolidate sempre humano na app.

Ver `reference.md` e `examples.md`.