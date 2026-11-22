# F2 — Prompt get-review (F04_B07)

**Entrada:** `redaction/F04_B07/REDACAO-F04_B07.md` + pacote materializado.

## Pré-verificação (CLI)

```powershell
python scripts/f2_review_report.py `
  --draft "redaction\F04_B07\REDACAO-F04_B07.md" `
  --block-json "redaction\F04_B07\F04_B07_discussion_llm.json"
```

Exit code `0` ⇒ todas as frases `must_include` (ready/approved) aparecem no rascunho — ainda assim validar semântica e glossário.

## Prompt (copiar)

```text
MODO: get-review / F2
Âmbito: bloco F04_B07 — comparar REDACAO-F04_B07.md com export GET-LLM e terminology_discussion_llm.md.

Objectivo:
- Inconsistências vs must_include, premissas e glossário (avoid_terms / preferred).
- PROPOSE: GET-PACKAGE só se o registo precisar de correcção; não reescrever o capítulo inteiro no chat.
- Secção «Não corrigir no GET» para pura redacção.

Saída: lista priorizada + pacote JSON se necessário.
```

Registar em [micro-F2-retro-F04_B07.md](micro-F2-retro-F04_B07.md).