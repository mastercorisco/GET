# F2 — Fecho M2 produção (humano)

Tooling M2 (dry-run) está fechado — ver [micro-F2-retro-F04_B07.md](micro-F2-retro-F04_B07.md).

## Checklist

1. [ ] Redação final `REDACAO-F04_B07.md` (get-write-spec), não só `f2_draft_from_export`.
2. [ ] `f2_m2_gate.py` no rascunho final (must_include + glossário).
3. [ ] Sessão **get-review** — [micro-F2-review-session-F04_B07.md](micro-F2-review-session-F04_B07.md).
4. [ ] GET-PACKAGE de correcções (se necessário); **não** reimportar MD.
5. [ ] Actualizar [micro-F2-piloto-EXECUTION-LOG.md](micro-F2-piloto-EXECUTION-LOG.md) e GET_MACRO_PLAN §9 (M2 fechado).

## Arranque T2.0

```powershell
# Com servidor GET activo
python backend/scripts/t2_readiness_check.py --project-id <UUID>
```

Critérios completos: [micro-T2-mcp-get-server.md](micro-T2-mcp-get-server.md).