# GET Gerador de Especificações Funcionais — pacote de planeamento para Cursor

Este pacote contém a definição de produto, decisões arquiteturais, contratos JSON, exemplos e instruções necessárias para o Cursor produzir primeiro um plano detalhado e, apenas após aprovação humana, iniciar a implementação.

## Objetivo do produto

O GET Gerador de Especificações Funcionais é uma aplicação web local, sem IA incorporada, destinada a armazenar, organizar, versionar, relacionar, validar e exportar conhecimento técnico de cadernos de encargos. A aplicação exporta JSON para discussão ou redação em LLM externas e reimporta apenas JSON estruturado para revisão humana.

## Ordem recomendada no Cursor

1. Abrir esta pasta como workspace.
2. Iniciar um novo chat Agent/Plan.
3. Anexar ou referenciar `CURSOR_MASTER_PROMPT.md`.
4. Pedir ao Cursor para ler todos os ficheiros indicados no prompt.
5. Exigir como primeira entrega apenas:
   - inventário de requisitos;
   - questões bloqueantes;
   - arquitetura proposta;
   - modelo de dados;
   - plano faseado;
   - riscos;
   - critérios de aceitação;
   - lista de ficheiros a criar.
6. Não autorizar código antes de rever e aprovar o plano.

## Conteúdo

- `CURSOR_MASTER_PROMPT.md`: prompt principal para o Cursor.
- `.cursor/rules/get-knowledge-studio.mdc`: regras persistentes do workspace.
- `docs/GET_APP_SPECIFICATION.md`: especificação funcional consolidada.
- `docs/IMPLEMENTATION_PLAN_TEMPLATE.md`: estrutura obrigatória do plano.
- `docs/DATA_MODEL.md`: modelo conceptual e entidades.
- `ARCHITECTURE_DECISIONS.json`: decisões encerradas no processo Grill Me.
- `BACKLOG.json`: épicos, histórias e critérios de aceitação do MVP.
- `schemas/*.schema.json`: contratos JSON Draft 2020-12.
- `examples/*.json`: exemplos válidos de mestre e fascículo autónomo.

## Regra central

A base de dados SQLite é a fonte de verdade. JSON e Markdown são artefactos derivados. A aplicação não chama LLM, não gera texto técnico e não converte Markdown em Word.

## Execução local (Fase 1 — E01)

```bash
# Backend (127.0.0.1:4810)
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --host 127.0.0.1 --port 4810

# Frontend (127.0.0.1:4811, proxy /api → backend)
cd frontend
npm install
npm run dev
```

Ou:

- **Windows:** duplo clique em `scripts\run_local.bat` (ou executar na linha de comandos)
- **Linux/macOS:** `scripts/run_local.sh`

### Testes

```bash
cd backend && pytest
cd frontend && npm test
cd e2e/playwright && npm install && npx playwright test
```

Documentação de implementação: `docs/PLAN.md`, revisão: `docs/PLAN_REVIEW_CHECKLIST.md`.
