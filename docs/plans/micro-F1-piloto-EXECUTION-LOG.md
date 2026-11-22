# F1 — Registo de execução (M1)

| Campo | Valor |
|--------|--------|
| Bloco activo | [micro-F1-bloco-F04_B07-grill.md](micro-F1-bloco-F04_B07-grill.md) |
| Bloco estável (opcional) | F01_B01 — 4/4 `ready` |
| Estado | **Fechado** (M1 2026-11-22 — 6/8 `ready` em F04_B07) |

## Ferramentas

| Script | Uso |
|--------|-----|
| `f1_block_preflight.py` | Status por ponto + `--export` |
| `f1_patch_block_point.py` | Dry-run / patches JSON (`--patches`) |
| `f1_ready_check.py` | Harness; `--apply-ready --confirm` (confirmação explícita) |
| `f0_roundtrip_apply.py` | Import/merge/consolidate (`--accept auto` em bloco) |

## Dry-run grill (opcional)

```powershell
python scripts/f1_patch_block_point.py "exports\PKG-BLK-F04_B07\F04_B07_package.json" `
  --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 `
  --title-contains "brownfield" `
  --append-guidance "Coordenar desmontagens com janelas operacionais aprovadas pela exploração." `
  --out "imports\f1_dryrun_f04_b07.json"
python scripts/f0_roundtrip_apply.py "imports\f1_dryrun_f04_b07.json" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
```

## Dry-run 2026-11-22

- Ficheiro: `imports/f1_dryrun_f04_b07.json`
- Ponto: Execução brownfield — +1 `development_guidance`
- Backup consolidate: `df61c5f5-12d2-4d39-801e-ecad7b9bd0f7`

## Ciclo grill (fixture / agente 2026-11-22)

- Ficheiro patches: [fixtures/f1_grill_F04_B07_patches.json](fixtures/f1_grill_F04_B07_patches.json)
- JSON: `imports/f1_grill_f04_b07.json` (workspace testes)
- 3× `point_update` consolidados · backup `5d1235f6-0089-4cd5-aeff-92edb84dc918`
- `f1_ready_check`: **5 candidatos** a `ready` (harness OK; status ainda draft/incomplete)

```powershell
python scripts/f1_patch_block_point.py "exports\PKG-BLK-F04_B07\F04_B07_package.json" `
  --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 `
  --patches ..\docs\plans\fixtures\f1_grill_F04_B07_patches.json `
  --out "imports\f1_grill_f04_b07.json"
python scripts/f0_roundtrip_apply.py "imports\f1_grill_f04_b07.json" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
python scripts/f1_ready_check.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --block F04_B07
```

## Piloto LLM (get-grill)

- [x] Ciclo proposta+import (fixture ou sessão)
- [ ] Sessão adicional com [micro-F1-grill-session-prompt.md](micro-F1-grill-session-prompt.md) se quiser enriquecer mais pontos
- [x] Marcar `ready` — `f1_ready_check --apply-ready --confirm` (5 pontos 2026-11-22)

## Definition of Done M1

- [x] ≥1 ciclo grill+import documentado
- [x] Pontos alvo com harness validável na app
- [x] `ready` confirmado (`--confirm`) nos candidatos draft/incomplete