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
- Bloco `node_id`: `3a5c2f6d-0e18-418b-abe6-9dbd228b1d9b`
- Export: `exports/PKG-BLK-F01_B01/F01_B01_package.json` (`export_id` **PKG-BLK-F01_B01**)
- **Estado 2026-11-22:** 4/4 pontos já `ready` — M1 mínimo cumprido; grill aqui = refino de harness (opcional). Piloto grill com lacunas: [micro-F1-bloco-F04_B07-grill.md](micro-F1-bloco-F04_B07-grill.md)

## Passos

1. get-orient: confirmar F01 estável; listar pontos `draft`/`incomplete` em F01_B01 (`GET /api/projects/{id}/summary` ou export bloco).
2. Export GET-PACKAGE `scope.kind=block` para F01_B01.
3. Sessão **get-grill** (modo grill me conforme skill).
4. `validate_get_package_file.py` → import → aceitar propostas **pontos/premissas** (não estrutura).
5. Consolidate → validação app → marcar **`ready`** manualmente ponto a ponto.

## Entrega M1

≥1 bloco (F01_B01) com pontos alvo em `ready`, sem alertas bloqueantes.

Skill: `agent-skills/get-grill/` — [micro-get-grill-skill.md](micro-get-grill-skill.md).