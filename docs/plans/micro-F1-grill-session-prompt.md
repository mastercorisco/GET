# F1 — Prompt get-grill (F04_B07)

Usar com `exports/PKG-BLK-F04_B07/F04_B07_package.json`. Modo: **F0-content-block** ([ritual](micro-F0-import-ritual.md)).

## Foco sugerido (pré-voo 2026-11-22)

| Ponto | status | Sugestão grill |
|-------|--------|----------------|
| Destino dos materiais… | incomplete | fechar `open_questions` com lacunas honestas ou reforçar `must_include` |
| Execução brownfield | draft | `development_guidance` + interfaces operacionais |
| Cablagem desativada | draft | distinção cabo reserva vs resíduo |
| Conservar/reutilizar | draft | critérios sem inventar valores |

**Não** alterar `rules_hash`, `export_id`, `scope`, nem marcar `ready`/`approved`.

## Prompt (copiar)

```text
MODO: F0-content-block / get-grill
Input: GET-PACKAGE bloco F04_B07 anexo (scope.kind=block).

Objetivo desta sessão:
- Enriquecer harness de 1–3 pontos em status draft ou incomplete (prioridade: sort_order 1 e 4).
- Melhorar core_idea, intended_outcome, must_include e open_questions com objectos tipados.
- Não reorganizar fascículo; não editar editable_knowledge.
- Não propagar status ready/approved — o engenheiro marca na UI.

Saída: JSON GET-PACKAGE completo; rules_hash inalterado.
```

## Pós-sessão

```powershell
python scripts/validate_get_package_file.py "<json>" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
python scripts/f0_roundtrip_apply.py "<json>" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
python scripts/f1_ready_check.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --block F04_B07
```

`f0_roundtrip_apply` em modo **auto** aceita propostas de pontos/premissas em pacotes bloco.

Dry-run repetível com fixture: `docs/plans/fixtures/f1_grill_F04_B07_patches.json` + `f1_patch_block_point.py --patches`.

Registar em [micro-F1-piloto-EXECUTION-LOG.md](micro-F1-piloto-EXECUTION-LOG.md).