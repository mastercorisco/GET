# Micro-plano — servidor MCP GET (T2 / F4)

**Macro:** [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) §3.2, §8 anti-objectivos.  
**ADR:** ADR-063.  
**Matriz:** [docs/mcp/TOOL_CATALOG.md](../mcp/TOOL_CATALOG.md).

## Objetivo

Definir o servidor MCP local como **proxy HTTP** para a API FastAPI existente, alinhado a todas as skills do [GET_SKILLS_PLAN.md](../GET_SKILLS_PLAN.md), **sem implementar código neste incremento**.

## Fora de âmbito (este plano e até checklist T2.0)

- Pasta `mcp-get/`, dependências MCP, `pyproject` novo.
- Docker, cloud, autenticação multiutilizador.
- Escrita MCP antes de **M2** fechado.
- Staging tipado dedicado MCP (onda **T3** — alinhado a GET-PACKAGE).
- Alterações FastAPI só “por MCP” (excepto gaps listados no catálogo).

## Arquitectura alvo

```text
Agente (Cursor / Claude) ──stdio──► mcp-get/ ──HTTP──► FastAPI 127.0.0.1/api
                                              ╳ SQLite directo
```

| Onda | Conteúdo |
|------|----------|
| **T2.0** | stdio + tools só leitura (health, search, list/get) |
| **T2.1** | POST/PATCH/DELETE com parâmetro `confirm` obrigatório |
| **T3** | Tools de proposta/staging alinhadas a import GET-PACKAGE |

## Esqueleto futuro (referência)

```text
mcp-get/
  README.md
  pyproject.toml          # mcp SDK + httpx
  src/get_mcp/server.py
  src/get_mcp/client.py   # thin HTTP
  tests/                  # mock httpx
```

Exemplo de config Cursor: documentar em `mcp-get/README.md` quando existir; **não** commitar segredos.

## Critérios para iniciar implementação (T2.0)

- [ ] **M2** piloto: get-write-spec → get-review → GET-PACKAGE aceite.
- [ ] ≥2 skills além de get-orient / get-lexicon validadas em sessão real (ex. get-grill).
- [ ] Servidor GET estável no workspace; base URL documentada.
- [ ] Engenheiro aceita que exports **ou** MCP bastam para leitura (não ambos obrigatórios).

## Critérios T2.1 (escrita)

- [ ] Padrão `confirm` alinhado a `POST /backups/{id}/restore?confirm=true`.
- [ ] `confirm` em DELETE terminologia (produto).
- [ ] Descrição de cada tool de escrita avisa: confirmação humana na app.

## Testes futuros

- Unitários: mock `httpx` — cada tool mapeia URL e método correctos.
- Integração opcional: workspace pytest temporário + TestClient ou servidor local.
- **Sem** testes LLM no pacote MCP.

## Estado

| Campo | Valor |
|-------|--------|
| ADR-063 | **Aceite** (implementação **adiada**) |
| Código `mcp-get/` | **Não iniciado** |
| Gatilho | Fecho **M2** + checklist T2.0 acima |

## Relação com agent-skills

- Skills Cursor: fonte em [`agent-skills/`](../../agent-skills/); MCP é **opcional** em T2.
- Até T2: skills usam exports + `curl`/fetch a `/api` conforme SKILL.md.
- Ao implementar MCP: actualizar SKILL.md só para “pode usar tool X em alternativa a curl”, sem mudar comportamento canónico em GET_SKILLS_PLAN.