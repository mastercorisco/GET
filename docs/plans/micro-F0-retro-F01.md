# F0 — Retro F01 (piloto estrutura)

**Feito** 2026-11-22 — canal **dry-run** (script), não LLM. Plano: [micro-F0-piloto-structure.md](micro-F0-piloto-structure.md).

## Estado inicial

- **Data:** 2026-11-22
- **Canal de import:** GET-PACKAGE **fascicle** (F0-structure)
- **Sintoma:** Piloto controlado pós Phase A (incidente anterior em block package)
- **Ficheiro fonte:** `GET_aux/testes/imports/f0_dryrun_f01_structure.json` (mutação `f0_mutate_fascicle_structure.py`)
- **export_id base:** PKG-FASC-F01
- **Backup pós-consolidate:** `c063479f-42a2-48a6-87e8-451657fa5967` (criado na consolidate do piloto)

## Causa provável (histórico Phase A)

Sessões LLM com pacotes bloco “completo” e imports repetidos — ver Phase A.

## O que foi feito (este piloto)

- [x] Backup crítico antes do import (já existiam backups 2026-11-22)
- [x] Piloto F0-structure F01 (dry-run + `f0_roundtrip_apply.py`)
- **Notas:** 1 proposta `structure` aceite; 0 `conceptual_warnings`; título F01_B01 actualizado.

## Pilotos F0

### F0-structure

- Fascículo: **F01** (`753c0de0-a759-4a8c-8e13-96a1360e0754`)
- Alteração testada: title do bloco **F01_B01** → `Objeto e finalidade (piloto F0 dry-run)`
- Propostas: 1 structure **aceite** / 0 rejeitadas
- Re-export OK: **sim** (PKG-FASC-F01 actualizado após consolidate)
- `conceptual_warnings`: nenhum

### F0-content-block (opcional — outra sessão)

- Pendente

### F0-knowledge (opcional)

- Pendente

## Definition of Done F0

- [x] Árvore coerente na UI (título F01_B01 verificado na base)
- [x] editable_knowledge sem atalhos protected→editable (ciclo só estrutura)
- [x] ≥1 ciclo documentado (structure mínimo)
- [x] Checklist ritual aplicada (validate + import + grupo estrutura equivalente via CLI)

## Não repetir

1. Pacotes bloco “completo” misturando estrutura e harness no mesmo ciclo.
2. Import sem `export_id` / PKG-FASC fresco.
3. Aceitar em lote propostas fora do modo F0-*.

## Gate seguinte

- [x] Avançar **F1** — [micro-F1-bloco-F01_B01-grill.md](micro-F1-bloco-F01_B01-grill.md)
- Opcional: repetir piloto com prompt LLM ([micro-F0-llm-session-prompt.md](micro-F0-llm-session-prompt.md)) para validar fluxo humano+LLM.