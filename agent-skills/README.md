# GET — pacote agent-skills (Cursor)

Instruções operacionais para agentes externos (Cursor, Claude, …). **Não faz parte do backend**; consome exports e API de leitura em `127.0.0.1`.

| Documento canónico | Papel |
|--------------------|--------|
| [`docs/GET_SKILLS_PLAN.md`](../docs/GET_SKILLS_PLAN.md) | Comportamento e proibições |
| [`docs/plans/`](../docs/plans/README.md) | Micro-planos e pilotos |
| `agent-skills/<nome>/` | **Fonte** de cada skill (`SKILL.md` + referências) |
| [`.cursor/skills/`](../.cursor/skills/) | Cópia para descoberta automática no Cursor (gerada por sync) |

## Workflow de autor

1. Editar apenas ficheiros em `agent-skills/<skill>/`.
2. Sincronizar para Cursor:
   - Windows: `.\sync-to-cursor.ps1`
   - Unix: `./sync-to-cursor.sh`
3. Validar contrato: `python -m pytest tests -q` (a partir desta pasta).

## Testes

Testes de **contrato** (frontmatter, secções obrigatórias, sync byte-identical). Não avaliam qualidade de texto LLM.

## Smoke manual (API)

Com o servidor GET activo no workspace:

```text
curl "http://127.0.0.1:8000/api/terminology/search?q=termo&project_id=<uuid>"
```

## Roadmap de skills

| Skill | Estado no MANIFEST |
|-------|-------------------|
| get-orient | implementada |
| get-lexicon | implementada |
| get-grill, get-research, get-write-spec, get-review, get-decision | planeadas |