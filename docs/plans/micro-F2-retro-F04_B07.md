# F2 — Retro piloto F04_B07 (M2 dry-run)

| Campo | Valor |
|--------|--------|
| Data | 2026-11-22 |
| Tipo | Dry-run get-write-spec (script) + review determinística |

## Artefactos (workspace testes)

| Ficheiro | Notas |
|----------|--------|
| `redaction/F04_B07/REDACAO-F04_B07.md` | `f2_draft_from_export.py` — piloto, não redação final |
| `f2_review_report` | 30/30 `must_include` cobertos |

## Aprendizagens

- Pipeline M2: materialize → draft → review report → get-review (humano/LLM).
- Rascunho automático basta para validar tooling; redação real permanece sessão get-write-spec.

## GET-PACKAGE

- **Nenhum** neste dry-run (texto alinhado ao registo exportado).

## Definition of Done M2

| Critério | Dry-run | Produção |
|----------|---------|----------|
| MD gerado | Sim (script) | Pendente texto caderno final |
| Review documentado | Sim (30/30) | Repetir após redação humana |
| Contradições graves | Não detectadas (âmbito must_include) | get-review completo |