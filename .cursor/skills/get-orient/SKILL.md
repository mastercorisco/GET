---
name: get-orient
description: Ponto de situação GET só leitura sobre exports GET-LLM/GET-PACKAGE e pesquisa API sem import.
disable-model-invocation: true
---

# get-orient — ponto de situação (READ-ONLY)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (secção get-orient). Plano de piloto: `docs/plans/micro-get-orient-skill.md`.

## Modo

- Ciclo: **READ → REASON → ANSWER** (não PROPOSE por defeito).
- Sessão explícita: o utilizador pediu orientação, não grill nem redação.

## Contexto mínimo

1. Caminho do workspace GET activo (`GET_WORKSPACE_ROOT` ou `~/.get/app-config.json`).
2. Pelo menos um de:
   - `exports/EXP-LLM-…/manifest.json` + `master_{profile}_llm.json` (panorama), ou
   - pasta GET-PACKAGE fascículo/bloco (`PKG-FASC-…`, `PKG-BLK-…`).
3. Opcional: `GET /api/knowledge/search?q=…&scope_type=library` (servidor em `127.0.0.1`).
4. Confirmação verbal: «só orientação, não gerar JSON de import».

## Ritual

1. Confirmar modo get-orient.
2. Limitar respostas ao contexto fornecido; se faltar dado, dizer «não consta no contexto fornecido».
3. Responder com secções fixas (ver template abaixo).
4. Se surgir trabalho de edição → encerrar e sugerir nova sessão **get-grill** com GET-PACKAGE novo.

## Template de saída

```markdown
## Estado
(resumo factual do export/pesquisa)

## Lacunas
(o que falta no harness, refs, glossário, staging)

## Riscos de import
(mistura estrutura/conteúdo, volumes, conceptual_warnings se existirem)

## Próximo passo sugerido
(uma skill seguinte: F0 ritual, get-grill bloco X, export novo, etc.)
```

## Proibido

- Devolver GET-PACKAGE ou JSON de import como resposta por defeito.
- Marcar `ready`, `approved` ou alterar campos protegidos.
- Inventar contagens, UUIDs ou factos não presentes no export/pesquisa.
- Substituir pesquisa FTS/knowledge para afirmações que exijam citação exata de KI.

## Entradas por profundidade

| Nível | Artefacto |
|-------|-----------|
| Panorama | GET-LLM mestre + manifest |
| Fascículo | GET-LLM fascículo-índice ou GET-PACKAGE fascículo |
| Bloco | GET-PACKAGE bloco |
| Biblioteca | Knowledge search ou KI no mestre |

Ver também `reference.md` e `examples.md` nesta pasta.