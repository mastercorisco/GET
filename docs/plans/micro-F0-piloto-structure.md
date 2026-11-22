# F0 — Piloto estrutural (F01)

Versão: 1.0.0 · Fase: [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) F0 · Ritual: [micro-F0-import-ritual.md](micro-F0-import-ritual.md).

## Objetivo

Provar **roundtrip F0-structure** num fascículo real: export → alteração mínima à árvore → import → consolidate → re-export, **sem** misturar pontos, premissas ou `editable_knowledge`.

## Âmbito

| Campo | Valor |
|--------|--------|
| Workspace | `C:\PROGRAMACAO\GET_aux\testes` (`~/.get/app-config.json`) |
| Projecto | CTBJ — `976e3991-e64e-4306-99fe-4ac1e2230b52` |
| Fascículo piloto | **F01** — `node_id` `753c0de0-a759-4a8c-8e13-96a1360e0754` |
| Export GET-PACKAGE | `exports/PKG-FASC-F01/F01_package.json` (`export_id` **PKG-FASC-F01**) |
| Modo | **F0-structure** apenas |
| Alteração de teste | Ex.: corrigir **1** título de bloco ou ordem relativa mínima (documentar no retro) |

## Fora de âmbito

- Pacotes `scope.kind=block` “completo” (incidente Phase A — ver [micro-F0-phase-A-workspace-testes.md](micro-F0-phase-A-workspace-testes.md)).
- F0-content-block, F0-knowledge, get-grill, redação.
- Aceitar em lote sem revisão humana.

## Pré-voo (obrigatório)

1. **Backup crítico** na app (`backups/critical/`).
2. **Re-export** fascículo F01 na UI → anotar `export_id` e caminho em `exports/PKG-FASC-F01/`.
3. Sessão **get-orient** (READ only): confirmar subárvore F01 e estado de imports recentes.
4. Copiar checklist: `agent-skills/get-orient/checklist-f0.md`.
5. Pré-voo CLI (opcional): `python backend/scripts/f0_pilot_preflight.py --project-id <uuid> --fascicle F01 --export`
6. Snapshot M0: [micro-F0-orient-snapshot-CTBJ.md](micro-F0-orient-snapshot-CTBJ.md)
7. Dry-run sem LLM (opcional): [micro-F0-structure-dryrun.md](micro-F0-structure-dryrun.md) · prompt LLM: [micro-F0-llm-session-prompt.md](micro-F0-llm-session-prompt.md)

## Fluxo

```text
Backup
  → Export GET-PACKAGE fascículo F01 (notar export_id)
  → LLM modo F0-structure (prompt no ritual)
  → validate_get_package_file.py (estrito)
  → POST packages/import → rever conceptual_warnings (UI + API)
  → Merge → decidir propostas (filtro «estrutura» na UI)
  → Consolidate
  → Re-export F01 → verificar árvore na UI
```

### Validação CLI

```powershell
cd C:\PROGRAMACAO\GET\backend
python scripts/validate_get_package_file.py "<caminho\F01_*.json>" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
```

### APIs

- Import: `POST /api/projects/{id}/packages/import`
- Merge: `POST /api/projects/{id}/packages/imports/{import_id}/merge`
- Consolidate: `POST /api/projects/{id}/packages/merge/{merge_id}/consolidate`

## Critérios de aceitação

- [ ] Validação estrita do JSON sem erro.
- [ ] `conceptual_warnings` lidos (vazios ou explicados no retro).
- [ ] Apenas propostas de **estrutura** aceites neste ciclo.
- [ ] Árvore F01 coerente após consolidate.
- [ ] Novo export registado; `export_id` diferente do ciclo anterior.
- [ ] Retro preenchido: [micro-F0-retro-F01.md](micro-F0-retro-F01.md).

## Gate seguinte

- **F1:** [micro-F1-bloco-F01_B01-grill.md](micro-F1-bloco-F01_B01-grill.md) após DoD F0 no retro.
- Se falha conceptual de novo → documentar em retro e rever ritual; **não** avançar grill no mesmo fascículo instável.

## Referências

- Inventário Phase A: [micro-F0-phase-A-workspace-testes.md](micro-F0-phase-A-workspace-testes.md)
- Template retro: [micro-F0-retro-TEMPLATE.md](micro-F0-retro-TEMPLATE.md)