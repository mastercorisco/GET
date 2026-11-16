# Guia de interface GET (shell estático v1)

## Layout escolhido

**Mockup A+C:** barra superior de estado + menu lateral por fluxo + painel explorer (árvore documental + detalhe) na vista «Estrutura documental».

## Ficheiros

| Área | Caminho |
|------|---------|
| Shell HTML | [`backend/app/static/index.html`](../backend/app/static/index.html) |
| Estilos | [`backend/app/static/css/`](../backend/app/static/css/) |
| Entrada JS | [`backend/app/static/js/main.js`](../backend/app/static/js/main.js) |
| Lógica de domínio (transição) | [`backend/app/static/js/app/legacy-logic.js`](../backend/app/static/js/app/legacy-logic.js) |
| Rotas UI | [`backend/app/static/js/router.js`](../backend/app/static/js/router.js) |
| Árvore ASCII | [`backend/app/static/js/components/tree.js`](../backend/app/static/js/components/tree.js) |
| Tips (i) | [`backend/app/static/js/components/tip.js`](../backend/app/static/js/components/tip.js) |
| Rótulos PT | [`backend/app/static/js/labels.js`](../backend/app/static/js/labels.js) |
| Mockup de referência | [`backend/app/static/mockups/shell-mockup-a.html`](../backend/app/static/mockups/shell-mockup-a.html) |

Assets servidos em `GET /static/...` via FastAPI `StaticFiles`.

## Navegação

1. **Preparar workspace** — criar/abrir pasta de dados.
2. **Importação Excel** — modelo v1: validar, dry-run e consolidar (novo projecto ou activo).
3. **Biblioteca** — conhecimento transversal, referências, terminologia.
4. **Projecto** — criação, conhecimento do projecto, fichas, referências, overrides.
5. **Estrutura documental** — árvore ASCII, exportação MD/PDF/XMind, associações.
6. **Árvore técnica** — instâncias hierárquicas.
7. **Exportar / Reimportar** — ciclo LLM.
8. **Backups** — listagem e backup crítico.
9. **Diagnóstico** — metadados do workspace (avançado).

## Tips (i)

Botões junto a campos críticos; textos em `TIPS` em `tip.js`. Para novo campo: acrescentar entrada e mapear em `wireTips()`.

## Checklist smoke manual

- [ ] Abrir `http://127.0.0.1:4810/` — menu lateral após abrir workspace.
- [ ] Criar workspace; barra superior mostra caminho.
- [ ] Biblioteca: criar unidade + concluir revisão.
- [ ] Projecto: criar, fascículo + bloco — árvore ASCII visível.
- [ ] Exportar: publicar baseline + export mestre.
- [ ] Reimportar: upload JSON + merge (se fixture disponível).
- [ ] Excel: validar → dry-run → aplicar com `I_UNDERSTAND` (ou só validar se for teste).
- [ ] Estrutura: exportar Markdown com pontos resumo (projecto activo).
- [ ] Backups: criar backup crítico e listar.

## Evolução (React)

`api/client.js` concentra chamadas HTTP para reutilização com TanStack Query. `views/` espelha futuras rotas React.