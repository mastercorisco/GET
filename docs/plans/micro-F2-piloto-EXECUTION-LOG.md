# F2 — Registo de execução (M2)

| Campo | Valor |
|--------|--------|
| Pré-requisito | F1 M1 — bloco com pontos `ready` |
| Bloco piloto | **F04_B07** (CTBJ testes) |
| Estado | **Dry-run tooling OK** — redação final humana pendente |

## Ferramentas

| Script | Uso |
|--------|-----|
| `f2_m2_preflight.py` | Contagens exportáveis + `--export` GET-LLM (fascículo do bloco) |
| `f2_m2_materialize.py` | Copiar bloco + glossário para `redaction/{block}`; `--outline` |
| `f2_review_report.py` | Cobertura `must_include` no rascunho MD |
| `f2_draft_from_export.py` | Dry-run MD a partir do JSON export (não canónico) |
| Skills | `get-write-spec`, `get-review` |

## Pré-voo M2

```powershell
cd backend
python scripts/f1_ready_check.py --project-id <UUID> --block F04_B07
python scripts/f2_m2_preflight.py --project-id <UUID> --block F04_B07 --export
```

## Export 2026-11-22 (workspace testes)

- `f2_m2_preflight.py --export`
- ZIP: `exports/EXP-LLM-976e3991/llm_generation_discussion.zip`
- F04_B07: 6× `ready`, 2× `approved`; glossário presente no ZIP

## Kit redação (2026-11-22)

- `redaction/F04_B07/` no workspace testes (materialize + outline)
- Prompt: [micro-F2-write-session-F04_B07.md](micro-F2-write-session-F04_B07.md)

## Piloto ponta a ponta

- [x] Export GET-LLM com glossário no ZIP
- [x] Materializar inputs + esboço REDACAO
- [x] Dry-run texto: `f2_draft_from_export.py` → `REDACAO-F04_B07.md` (workspace)
- [x] `f2_review_report`: **30/30** must_include
- [ ] Sessão **get-write-spec** (redação caderno final)
- [ ] **get-review** semântico + glossário — [micro-F2-review-session-F04_B07.md](micro-F2-review-session-F04_B07.md)
- [ ] Correcções via GET-PACKAGE (se aplicável) — não reimportar MD

## Definition of Done M2

- [ ] Texto MD gerado a partir do ZIP
- [ ] Review documentado (lacunas ou OK)
- [ ] Sem contradições graves vs SQLite