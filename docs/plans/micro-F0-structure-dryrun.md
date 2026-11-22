# F0-structure — dry-run (sem LLM)

Prova o roundtrip **estrutural** antes ou em paralelo à sessão LLM. Alinhado a [micro-F0-piloto-structure.md](micro-F0-piloto-structure.md).

## Pré-requisitos

- `PKG-FASC-F01` actual (`f0_pilot_preflight.py --export`).
- Projecto CTBJ: `976e3991-e64e-4306-99fe-4ac1e2230b52`.

## Passos

```powershell
cd C:\PROGRAMACAO\GET\backend
$pkg = "C:\PROGRAMACAO\GET_aux\testes\exports\PKG-FASC-F01\F01_package.json"
python scripts/f0_mutate_fascicle_structure.py $pkg `
  --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 `
  --display-code F01_B01 `
  --title "Objeto e finalidade (piloto F0 dry-run)" `
  --out "C:\PROGRAMACAO\GET_aux\testes\imports\f0_dryrun_f01_structure.json"
python scripts/validate_get_package_file.py "C:\PROGRAMACAO\GET_aux\testes\imports\f0_dryrun_f01_structure.json" `
  --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
```

**Via app:** Reimportar → avisos → Rever → filtro Estrutura → Consolidar.

**Via CLI** (equivalente, `--accept structure-only`):

```powershell
python scripts/f0_roundtrip_apply.py "C:\PROGRAMACAO\GET_aux\testes\imports\f0_dryrun_f01_structure.json" `
  --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
```

1. Confirmar título F01_B01 na árvore (ou na base).
2. Re-export F01; anotar no [retro](micro-F0-retro-F01.md).

## Critério

- Uma proposta `proposal_kind=structure` aceite; título do bloco actualizado; sem propostas de knowledge/pontos neste ciclo.

## CI

O mesmo fluxo está coberto por `test_fascicle_get_package_f0_structure_roundtrip` em `backend/tests/integration/test_get_package.py`.