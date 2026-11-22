# F1 — Bloco F01_B01 (get-grill)

**Pré-requisito:** F0 fechado — [micro-F0-retro-F01.md](micro-F0-retro-F01.md) com DoD assinalado.

## Objetivo

Bloco **F01_B01** com pontos harness completos; caminho até `ready` (marcação **humana** na UI).

## Escopo

| Incluído | Excluído |
|----------|----------|
| get-orient → get-grill + get-research pontual | get-write-spec (F2) |
| Import modo **F0-content-block** (só este bloco) | Estrutura fascículo |
| `Reference` com path/URL quando aplicável | `approved` via import |

## Projecto

- CTBJ `976e3991-e64e-4306-99fe-4ac1e2230b52`
- Export: `PKG-BLK-F01_B01` (re-export imediato antes da sessão LLM)

## Passos

1. get-orient: confirmar F01 estável; listar pontos `draft`/`incomplete` em F01_B01 (`GET /api/projects/{id}/summary` ou export bloco).
2. Export GET-PACKAGE `scope.kind=block` para F01_B01.
3. Sessão **get-grill** (modo grill me conforme skill).
4. `validate_get_package_file.py` → import → aceitar propostas **pontos/premissas** (não estrutura).
5. Consolidate → validação app → marcar **`ready`** manualmente ponto a ponto.

## Entrega M1

≥1 bloco (F01_B01) com pontos alvo em `ready`, sem alertas bloqueantes.

Skill: `agent-skills/get-grill/` — [micro-get-grill-skill.md](micro-get-grill-skill.md).