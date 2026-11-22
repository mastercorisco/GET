# get-orient — skill de leitura (plano micro)

**Fase macro:** transversal (F0–F3); recomendada **antes** do piloto F1.  
**Pai:** [GET_SKILLS_PLAN.md](../GET_SKILLS_PLAN.md#get-orient--ponto-de-situação-só-leitura), [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) M0.

## Objetivo

Permitir perguntas ao **conteúdo** do GET (projecto e biblioteca) para perceber o ponto de situação **sem** ciclo de import nem confundir com get-grill.

## Fora de âmbito

- Implementação na app (LLM interna, MCP, dashboard).
- GET-PACKAGE na resposta por defeito.
- Commit ou staging automático.

## Entregáveis

| # | Entrega | Critério de aceitação |
|---|---------|------------------------|
| 1 | Secção canónica em GET_SKILLS_PLAN | Feito neste incremento de documentação |
| 2 | `agent-skills/get-orient/SKILL.md` + sync → `.cursor/skills/get-orient/` | Instruções READ-ONLY, lista de inputs, anti-padrões, exemplos de prompts |
| 3 | Checklist “contexto mínimo” na skill | Mestre LLM **ou** pacote bloco/fascículo + `project_id`; biblioteca via search ou KI no export |
| 4 | Piloto uma sessão | Engenheiro faz 3–5 perguntas sobre CTBJ; respostas citam apenas o fornecido; próximo passo nomeia skill seguinte (grill/F0) |

## Contexto mínimo para o agente

```text
1. Caminho do workspace GET activo (~/.get ou GET_WORKSPACE_ROOT).
2. Um de:
   - exports/EXP-LLM-…/manifest.json + project_master.json (panorama), ou
   - exports/PKG-FASC-…/ ou PKG-BLK-…/ (âmbito local).
3. Opcional: resultados de pesquisa (copiar da UI ou curl GET /api/knowledge/search).
4. Pergunta explícita: “só orientação, não gerar JSON de import”.
```

## Ritual de sessão

1. Confirmar modo **get-orient** (sem proposta).
2. Carregar contexto mínimo.
3. Responder com secções: **Estado** · **Lacunas** · **Riscos de import** · **Próximo passo sugerido**.
4. Se surgir trabalho de edição → fechar e abrir sessão get-grill com GET-PACKAGE novo.

## Dependências de produto (opcionais, melhoram a skill)

- `conceptual_warnings` no import (já v1).
- Relatório determinístico contagens (backlog macro §6).
- Export workbook actualizado antes de perguntas numéricas.

## Estado

| Campo | Valor |
|-------|--------|
| Documentação plano | 2026-11-21 |
| SKILL.md Cursor | **Feito** (`agent-skills/get-orient`) |
| Piloto utilizador | Pendente |