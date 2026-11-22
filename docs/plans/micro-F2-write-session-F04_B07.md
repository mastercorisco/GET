# F2 — Prompt get-write-spec (F04_B07)

**Export:** `exports/EXP-LLM-976e3991/llm_generation_discussion.zip` ou pasta materializada em `redaction/F04_B07/`.

## Materializar (repo / CLI)

```powershell
cd backend
python scripts/f2_m2_materialize.py --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52 --block F04_B07 --outline
```

Editar `redaction/F04_B07/REDACAO-F04_B07-outline.md` → guardar como `REDACAO-F04_B07.md` (fora do GET).

Dry-run (só tooling):

```powershell
python scripts/f2_draft_from_export.py "redaction\F04_B07\F04_B07_discussion_llm.json" --out "redaction\F04_B07\REDACAO-F04_B07.md"
```

## Prompt (copiar)

```text
MODO: get-write-spec / F2
Âmbito: bloco F04_B07 apenas (desmontagens e destino de equipamentos).

Inputs:
- F04_B07_discussion_llm.json + .md (export GET-LLM)
- terminology_discussion_llm.md (glossário vinculativo)

Objectivo:
- Redigir texto de caderno por ponto ready/approved, respeitando must_include e limits.
- Usar léxico do glossário; não inventar classes normativas sem open_question.
- Marcar "Sugestões não aprovadas" se llm_freedom=exploratory.

Saída: ficheiro REDACAO-F04_B07.md (Markdown). Não é GET-PACKAGE.
```

## Review

```powershell
python scripts/f2_review_report.py --draft "..\..\testes\redaction\F04_B07\REDACAO-F04_B07.md" --block-json "..\..\testes\redaction\F04_B07\F04_B07_discussion_llm.json"
```

Correcções ao registo → **get-review** + GET-PACKAGE, não reimportar o MD.

Registar em [micro-F2-piloto-EXECUTION-LOG.md](micro-F2-piloto-EXECUTION-LOG.md).