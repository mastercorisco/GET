# MCP GET — catálogo de tools (futuro)

**Estado:** documentação; **sem** implementação (ADR-063). Matriz de referência para `mcp-get/` quando T2 arrancar.

**Princípios:** cada tool chama **um** endpoint FastAPI ou indica leitura de export em disco **com caminho fornecido pelo utilizador** — o MCP não descobre o workspace sozinho.

Base URL: `http://127.0.0.1:<porta>/api` (servidor GET activo).

## Legenda

| Coluna | Significado |
|--------|-------------|
| **T2.0** | Leitura — implementação MCP fase inicial |
| **T2.1** | Escrita — só com `confirm=true` + confirmação humana na conversa |
| **Hoje** | Como as skills trabalham sem MCP |

## Matriz skill → tools

| Skill | T2.0 (leitura) | T2.1 (escrita + confirm) | Preferência hoje |
|-------|----------------|--------------------------|------------------|
| **get-orient** | `health`, `health/workspace`, `GET /projects`, `GET /projects/{id}`, `GET /knowledge/search`, `GET /imports` (staging, só leitura) | — | GET-LLM mestre + `manifest.json` |
| **get-grill** | `POST /packages/...` export, `GET` nós documentais, pontos do bloco | — (propostas em JSON, não SQLite) | GET-PACKAGE bloco/fascículo |
| **get-research** | `GET /references`, `GET /knowledge/{id}` | `POST /knowledge`, `POST /references` | corpus + refs na app |
| **get-lexicon** | `GET /terminology/search`, `GET /terminology` | `POST /terminology`, `POST .../terminology-overrides` | ZIP `terminology_*_llm.json` |
| **get-write-spec** | — (artefactos em disco) | — | ZIP GET-LLM completo |
| **get-review** | search + leitura pacote export | import via GET-PACKAGE (humano na UI; MCP não consolida) | MD redigido + export |
| **get-decision** | `GET /knowledge` (tipo decision) | `POST /knowledge` decision | biblioteca + pontos |

## Tools transversais (não ligadas a uma skill)

| Tool proposta | API / origem | Fase |
|---------------|--------------|------|
| `get_workspace_health` | `GET /health/workspace` | T2.0 |
| `list_projects` | `GET /projects` | T2.0 |
| `search_knowledge` | `GET /knowledge/search` | T2.0 |
| `search_terminology` | `GET /terminology/search` | T2.0 |
| `read_export_path` | Resource: ficheiro sob `{workspace}/exports/` (path explícito) | T2.0 |

## Gaps de produto (antes de MCP “completo”)

| Gap | Impacto nas tools | Backlog |
|-----|------------------|---------|
| `confirm` em DELETE terminologia | tool `delete_terminology` segura | macro §6 T2 |
| Relatório contagens / staging + último GET-LLM | `get_project_summary` | **feito** `GET /projects/{id}/summary` |
| Endpoint “último export LLM por projecto” | evita MCP listar filesystem | **feito** `GET .../llm-generation/latest` |

## Anti-padrões

- Tool que abre `get.db` ou executa SQL.
- Tool que consolida import sem revisão humana na app.
- Duplicar regras de negócio no MCP (validação fica na API).

Ver [micro-T2-mcp-get-server.md](../plans/micro-T2-mcp-get-server.md) para critérios de arranque e ondas T2/T3.