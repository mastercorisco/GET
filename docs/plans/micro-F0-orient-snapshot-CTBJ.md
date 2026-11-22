# M0 — Snapshot get-orient (CTBJ / workspace testes)

**Data:** 2026-11-22 · **Só leitura** — gerado a partir da base activa (`GET /api/projects/.../summary` + estrutura F01).

## Estado (determinístico)

| Métrica | Valor |
|---------|--------|
| Projecto | `976e3991-e64e-4306-99fe-4ac1e2230b52` |
| Pontos `ready` | 974 |
| Pontos `draft` | 4 |
| Pontos `incomplete` | 1 |
| Pontos `approved` | 2 |
| `needs_review` | 0 |
| Imports em staging | 0 |
| Merge sessions abertas | 0 |
| Último export (registo) | `EXP-LLM-976e3991` (llm_generation) |

## Fascículo piloto F0 — F01

| Campo | Valor |
|--------|--------|
| `node_id` | `753c0de0-a759-4a8c-8e13-96a1360e0754` |
| Título | Enquadramento e requisitos gerais |
| GET-PACKAGE pré-voo | `exports/PKG-FASC-F01/F01_package.json` (`export_id` **PKG-FASC-F01**) |

### Blocos F01 (pontos por bloco)

| Código | Pontos | Título |
|--------|--------|--------|
| F01_B01 | 4 | Objeto e finalidade |
| F01_B02 | 4 | Caracterização geral da CTBJ e contexto do projeto |
| F01_B03 | 4 | Definições, terminologia e abreviaturas |
| F01_B04 | 4 | Enquadramento normativo, regulamentar e contratual |
| F01_B05 | 4 | Princípios gerais da solução |
| F01_B06 | 4 | Requisitos gerais da contratação |

## Riscos de import (contexto Phase A)

- Incidente anterior associado a pacotes **bloco** “completo”, não a fascículo.
- Não existia `PKG-FASC-F01` em disco antes do pré-voo 2026-11-22 — **re-export obrigatório** antes de cada ciclo LLM.

## Próximo passo sugerido (macro)

1. Confirmar backup crítico na app.
2. Sessão LLM **F0-structure** sobre `F01_package.json` (alteração mínima de título/ordem).
3. `validate_get_package_file.py` → import → filtro **Estrutura** na UI → consolidate.
4. Preencher [micro-F0-retro-F01.md](micro-F0-retro-F01.md).

Repetir snapshot: `python backend/scripts/f0_pilot_preflight.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --fascicle F01`.