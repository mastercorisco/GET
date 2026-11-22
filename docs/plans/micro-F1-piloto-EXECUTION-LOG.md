# F1 — Registo de execução (M1)

| Campo | Valor |
|--------|--------|
| Bloco activo | [micro-F1-bloco-F04_B07-grill.md](micro-F1-bloco-F04_B07-grill.md) |
| Bloco estável (opcional) | F01_B01 — 4/4 `ready` |
| Estado | **Em curso** (dry-run grill 2026-11-22 feito) |

## Ferramentas

| Script | Uso |
|--------|-----|
| `f1_block_preflight.py` | Status por ponto + `--export` |
| `f1_patch_block_point.py` | Dry-run mínimo (guidance) sem LLM |
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

## Piloto LLM (get-grill)

- [ ] Sessão com [micro-F1-grill-session-prompt.md](micro-F1-grill-session-prompt.md)
- [ ] Import + consolidate
- [ ] Marcar `ready` na UI nos pontos alvo

## Definition of Done M1

- [ ] ≥1 ciclo grill+import documentado
- [ ] Pontos alvo com harness validável na app
- [ ] `ready` humano nos pontos escolhidos