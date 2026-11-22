# F2 — Registo de execução (M2)

| Campo | Valor |
|--------|--------|
| Pré-requisito | F1 M1 — bloco com pontos `ready` |
| Bloco piloto | **F04_B07** (CTBJ testes) |
| Estado | **Em curso** (export GET-LLM 2026-11-22) |

## Ferramentas

| Script | Uso |
|--------|-----|
| `f2_m2_preflight.py` | Contagens exportáveis + `--export` GET-LLM (fascículo do bloco) |
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

## Piloto ponta a ponta

- [x] Export GET-LLM com glossário no ZIP
- [ ] Sessão **get-write-spec** (MD fora do GET)
- [ ] **get-review** contra pontos + glossário
- [ ] Correcções via GET-PACKAGE (se aplicável) — não reimportar MD

## Definition of Done M2

- [ ] Texto MD gerado a partir do ZIP
- [ ] Review documentado (lacunas ou OK)
- [ ] Sem contradições graves vs SQLite