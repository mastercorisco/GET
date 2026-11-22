# get-lexicon — skill glossário (plano micro)

**Macro:** T1 — [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) §3.2, §9.  
**API:** [micro-T1-terminology-search.md](micro-T1-terminology-search.md) (ADR-062).  
**Pacote Cursor:** `agent-skills/get-lexicon/` → sync `.cursor/skills/get-lexicon/`.

## Objetivo

Alinhar vocabulário técnico e propor candidatos `TerminologyConcept` / overrides sem gravar na app.

## Fora de âmbito

- MCP; POST automático na API; reimport do glossário ZIP.

## Entregáveis

| # | Entrega | Critério |
|---|---------|----------|
| 1 | `agent-skills/get-lexicon/SKILL.md` | READ + PROPOSE; proíbe POST sem confirmação |
| 2 | `examples.md` com JSON candidatos | Formato documentado |
| 3 | Testes contrato `agent-skills/tests` | Secções e frontmatter |
| 4 | Piloto manual | Search + proposta JSON; registo humano na UI |

## Estado

| Campo | Valor |
|-------|--------|
| SKILL.md | `agent-skills/get-lexicon` |
| Piloto utilizador | Pendente |