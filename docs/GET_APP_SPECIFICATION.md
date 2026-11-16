# Especificação funcional consolidada — GET Gerador de Especificações Funcionais

## 1. Finalidade

O GET Gerador de Especificações Funcionais é uma aplicação web local para armazenamento, organização, versionamento, relacionamento, validação e exportação de conhecimento técnico destinado à elaboração de cadernos de encargos.

A aplicação não produz texto com IA. O conhecimento é exportado em JSON para utilização manual numa LLM externa, como Microsoft Copilot ou Claude. A LLM poderá discutir e evoluir o conhecimento e devolver um JSON estruturado. O utilizador reimporta esse JSON, revê as diferenças e aprova seletivamente as alterações. O texto desenvolvido pela LLM deverá ser entregue separadamente em Markdown e poderá ser transformado posteriormente em Word por outra ferramenta.

## 2. Princípios do produto

1. **Fonte de verdade:** base de dados SQLite local.
2. **Separação:** conhecimento, estrutura documental, estrutura técnica e texto externo são objetos distintos.
3. **Reutilização:** Biblioteca EDA comum + conhecimento específico por projeto.
4. **Identidade:** UUID imutável, código legível mutável, aliases históricos.
5. **Versionamento:** revisões imutáveis, rascunhos temporários e baselines reproduzíveis.
6. **Intercâmbio:** JSON canónico; Markdown apenas para leitura; ZIP opcional.
7. **Controlo humano:** nenhuma alteração importada é consolidada sem aprovação.
8. **Determinismo:** exportações derivam de versões fixadas e regras explícitas.
9. **Aplicabilidade progressiva:** âmbito estruturado, condições opcionais e nota textual.
10. **Sem IA interna:** sem chamadas a modelos, embeddings, agentes ou geração textual.

## 3. Utilizador e execução

- Primeira versão individual e local.
- Aplicação web local em `127.0.0.1`.
- Sem autenticação no MVP.
- O utilizador local é registado apenas para proveniência.
- Operação offline obrigatoriamente possível.
- **Aparência da interface:** tema, densidade e tipografia são preferências **locais da máquina** (`~/.get/ui-preferences.json`); não entram em exportações JSON nem no SQLite do workspace. O nível de ajuda contextual permanece nas preferências do workspace.

### 3.1 Catálogo de ajuda (v1.3.0) e método

Narrativa funcional consolidada: [GET_METHOD.md](GET_METHOD.md) (estruturar no GET → LLM externa → revisão humana).

**Edição externa dos textos:** exportar `catalogs/get_help_editorial.pt-PT.json` com `python backend/scripts/export_help_editorial.py`, rever fora do repo, e voltar a importar com `python backend/scripts/import_help_editorial.py` (incrementa patch de `catalog_version`). A app continua a usar apenas `get_help_catalog.pt-PT.json`.

Ficheiro `catalogs/get_help_catalog.pt-PT.json`, servido por `GET /api/catalogs/help`. Inclui bloco `method` (princípio, fluxo, semântica do pacote exchange, governação). Por campo: `purpose_in_app`, `workflow_context`, `when_to_use`, `what_happens_next`, `related_concepts`, `related_screen`, `common_confusions`. Conceitos incluem `role_in_get` e `not_this`. Guias de ecrã usam `audience_note` e `purpose_steps`. O popup (i) segue a narrativa GET → fluxo → definição → exemplos; painel de preparação do bloco expõe o método. Não há geração de ajuda por LLM em runtime.

## 4. Áreas funcionais

### 4.1 Biblioteca EDA

Contém conhecimento reutilizável:

- factos;
- princípios;
- requisitos;
- decisões reutilizáveis;
- fundamentações;
- exemplos;
- recomendações;
- questões pendentes;
- exclusões;
- instruções de elaboração;
- vocabulário controlado;
- dicionário EDA de tags;
- classes de sistemas, equipamentos e funções;
- referências e fichas normativas;
- modelos de projeto;
- perfis de instruções;
- tipos de relação.

### 4.2 Projetos

Cada projeto contém:

- identidade e contexto;
- tipo de intervenção;
- âmbito, exclusões e condicionantes;
- estrutura documental;
- instâncias técnicas;
- referências a versões da biblioteca;
- variantes locais;
- funções, interfaces, requisitos, decisões e questões pendentes;
- disposições de aplicabilidade;
- baselines, exportações e importações.

### 4.3 Vistas coordenadas

- Vista documental: fascículos, blocos, secções e subsecções.
- Vista técnica: sistemas, equipamentos, funções e interfaces.
- Vista de conhecimento: unidades, relações, referências, estados e aplicabilidade.

A seleção de um objeto numa vista deve apresentar as relações relevantes das restantes vistas.

## 5. Captura do conhecimento

Existem duas entradas para o mesmo modelo:

1. criação direta na Biblioteca EDA;
2. criação contextual num projeto ou bloco.

Estrutura mínima obrigatória:

- título;
- conteúdo em Markdown limitado;
- contexto de origem.

A classificação pode iniciar-se como `unclassified` e ser completada progressivamente.

Tipos iniciais:

- `fact`;
- `principle`;
- `requirement`;
- `decision`;
- `rationale`;
- `example`;
- `recommendation`;
- `open_question`;
- `exclusion`;
- `authoring_instruction`;
- `unclassified`.

## 6. Estados

Três dimensões independentes:

### Maturidade

- `captured`;
- `structured`;
- `reviewed`;
- `mature`.

### Aprovação

- `unreviewed`;
- `proposed`;
- `confirmed`;
- `approved`;
- `rejected`.

### Ciclo de vida

- `active`;
- `superseded`;
- `withdrawn`;
- `archived`.

A interface apresenta estados resumidos calculados, sem perder as três dimensões.

## 7. Fichas estruturadas opcionais do MVP

1. Função de controlo.
2. Interface.
3. Requisito.
4. Decisão.
5. Questão pendente.

Os parâmetros técnicos mantêm-se como texto livre no MVP. Não existe validação automática de unidades ou gamas numéricas.

## 8. Estrutura documental

- Árvore genérica baseada em `parent_id`.
- Tipos: `fascicle`, `block`, `section`, `subsection`.
- Quatro níveis recomendados; aviso a partir do quinto.
- Numeração calculada por posição.
- Numeração congelada por baseline.
- IDs permanentes são independentes dos códigos `F04_B12`.
- A LLM pode propor alterações estruturais apenas dentro do fascículo exportado.

## 9. Estrutura técnica

- Catálogo reutilizável de classes.
- Instâncias específicas por projeto.
- Separação entre sistema, equipamento e função.
- Campos opcionais para referência funcional, produto e localização.
- Não implementar integralmente IEC 81346 como obrigação no MVP.

## 10. Relações

Vocabulário controlado extensível. Relações iniciais:

- `depends_on`;
- `supports`;
- `implements`;
- `constrains`;
- `conflicts_with`;
- `supersedes`;
- `derived_from`;
- `example_of`;
- `applies_to`;
- `verified_by`;
- `referenced_by`.

Cada tipo define direção, inversa, simetria e impacto na exportação. A app impede autorreferências e sinaliza ciclos de dependência.

## 11. Associação a blocos

A associação é qualificada, sem duplicar a unidade de conhecimento. Papéis iniciais:

- `mandatory_content`;
- `supporting_context`;
- `constraint`;
- `example`;
- `cross_reference`;
- `verification_basis`;
- `open_issue`;
- `excluded_content`.

Cada associação pode definir instrução de utilização, ordem, relevância e conteúdo a incluir na exportação.

## 12. Aplicabilidade e exclusões

Aplicabilidade progressiva:

- âmbito estruturado simples;
- condições formais opcionais;
- nota explicativa.

Resultados:

- `applicable`;
- `not_applicable`;
- `requires_review`;
- `unknown`.

Disposições de associação:

- `included`;
- `included_as_context`;
- `excluded_out_of_scope`;
- `not_applicable`;
- `addressed_elsewhere`;
- `rejected_by_decision`;
- `pending_assessment`;
- `superseded_locally`.

A omissão nunca equivale a exclusão ou eliminação.

## 13. Normas e referências

Qualquer fonte pode ser registada como referência genérica. Normas relevantes podem ativar ficha normativa com:

- código;
- organismo;
- edição;
- ano;
- estado do ciclo de vida;
- disponibilidade interna;
- localização;
- aplicabilidade;
- papel contratual;
- cláusulas relevantes;
- interpretação EDA;
- evidência requerida;
- estado de verificação.

Papéis:

- `informative_reference`;
- `design_basis`;
- `contractual_requirement`;
- `compliance_target`;
- `guidance_only`.

Associar uma norma não transforma automaticamente todo o respetivo conteúdo em requisito.

## 14. Terminologia

Vocabulário controlado reutilizável com:

- termo preferencial;
- definição;
- idioma;
- sigla;
- sinónimos;
- termos a evitar;
- tradução técnica;
- domínio;
- referências;
- exemplos;
- versões.

Projetos podem guardar termos legados e exceções. O dicionário de tags EDA é um objeto próprio.

## 15. Modelos de projeto

Projetos são criados a partir de modelos versionados. Primeiro modelo:

**Central de produção de energia elétrica — remodelação brownfield do sistema de comando e controlo.**

O modelo fornece:

- estrutura documental inicial;
- perfil-base de elaboração;
- princípios EDA;
- classes sugeridas;
- regras de validação;
- questões de configuração.

Atualizações do modelo não alteram projetos existentes automaticamente.

## 16. Perfis de instruções

Perfil-base versionado, complementado por projeto e fascículo. Instruções protegidas não podem ser contrariadas sem confirmação explícita.

Perfil técnico base:

- Português de Portugal;
- tom de engenheiro eletrotécnico sénior;
- automação industrial e centrais de produção;
- escrita técnica e contratual;
- não inventar parâmetros;
- não inventar exigências normativas;
- preservar decisões confirmadas;
- identificar lacunas;
- separar requisito, fundamentação e informação;
- saída Markdown previsível para processamento posterior.

## 17. Exportações

### Formatos

- JSON: canónico e reimportável.
- Markdown: leitura humana, não reimportável.
- ZIP: pacote opcional.

### Perfil Discussão

Inclui conhecimento confirmado, propostas, rascunhos selecionados, alternativas, decisões, questões, exclusões relevantes e instruções para debate.

### Perfil Redação

Inclui definições validadas, requisitos, restrições, terminologia, lacunas e contrato editorial. Não apresenta propostas como obrigações confirmadas.

### JSON mestre

Consolidado, mas seletivo: contexto global completo, estrutura, decisões transversais, sistemas resumidos e manifesto de fascículos.

### Fascículo autónomo

Inclui contexto suficiente para ser compreendido isoladamente, distinguindo contexto protegido e conhecimento editável.

### Exportação GET-LLM por bloco

Contrato `get_llm_export.schema.json` (GET-LLM 1.0): JSON **completo** para geração de texto na LLM externa, com códigos documentais **live** (sem baseline). Inclui projecto (incl. `project.llm_context_json` opcional), fascículo, bloco, unidades de conhecimento, normas, questões abertas, regras de geração e secção `preparation` (pontos, premissas, contexto de apoio). Cada exportação grava **JSON + Markdown** derivado (Markdown não reimportável). Distinto do roundtrip mestre/fascículo.

### Pacote GET-LLM em camadas (ecrã Exportar)

`POST /api/projects/{id}/exports/llm-generation`: gera **mestre** (`export_type: project_master`), **fascículo-índice** (`export_type: fascicle`, com `block_manifest[]` e hashes) e **ficheiros de bloco** (`export_type: block`) apenas para blocos com pontos exportáveis (`ready`/`approved`, ou rascunhos se `include_draft`). Artefactos em `{workspace}/exports/EXP-LLM-…/` e ZIP `llm_generation_{profile}.zip` com `manifest.json` (schema `GET-LLM-PACKAGE`). **Não reimportável**; ortogonal ao roundtrip mestre/fascículo (que continua a exigir baseline). Âmbito opcional: projecto inteiro ou um fascículo.

### Exportação estrutural legível

Independente do ciclo LLM (JSON/ZIP): a partir do ecrã **Estrutura documental**, o utilizador pode gerar **Markdown, PDF ou XMind** com a árvore documental do projecto (códigos **live** do SQLite) ou de uma **subárvore** (fascículo seleccionado). Opções: modelo estrutural do bloco; pontos de desenvolvimento (nenhum, resumo, completo); premissas resolvidas nos pontos completos. Artefactos em `{workspace}/exports/document-structure/`; **não reimportáveis**.

## 18. Política de edição no pacote

Modos:

- `read_only`;
- `propose_changes`;
- `editable`;
- `structure_only`;
- `reference_only`;
- `excluded`.

Campos sempre protegidos:

- ID;
- versão de origem;
- proveniência;
- aprovação;
- ciclo de vida.

Novos objetos entram como propostas. Remoções são propostas explícitas; nunca são inferidas por omissão.

## 19. Reimportação

1. Ficheiro entra em staging.
2. Validar sintaxe e schema.
3. Migrar versões suportadas numa cópia temporária.
4. Rejeitar versão futura desconhecida.
5. Quarentenar unidades com erros localizados.
6. Comparar base, atual e devolvido.
7. Agrupar alterações por unidade.
8. Exigir confirmação para campos protegidos, decisões confirmadas, eliminações e conflitos.
9. Escolher destino: projeto, biblioteca, pendente ou rejeitado.
10. Criar novas revisões.
11. Analisar impacto e marcar conteúdo potencialmente desatualizado.
12. Recompilar exportações quando solicitado.

## 20. Duplicados

Deteção determinística por título normalizado, código, tipo, âmbito, relações, referências e FTS5. Nunca fundir automaticamente. Fusões preservam aliases, relações, proveniência e histórico.

## 21. Pesquisa

- Texto integral com SQLite FTS5.
- Filtros por biblioteca/projeto, tipo, sistema, referência, estado, ficha, questões pendentes, reutilização, revisão e baseline.
- Sem embeddings ou pesquisa semântica no MVP.

## 22. Edição

- Autosave em rascunho.
- Conclusão explícita cria revisão.
- Possibilidade de descartar rascunho.
- Exportação usa revisões concluídas, salvo inclusão deliberada de rascunhos no perfil Discussão.

## 23. Baselines

Baseline imutável que fixa:

- revisões de conhecimento;
- versão da biblioteca;
- estrutura e numeração;
- sistemas e instâncias;
- referências;
- perfis;
- schemas;
- validações;
- manifesto de exportações.

## 24. Backups e workspace

Workspace separado da aplicação. Backups:

- antes de importações e alterações estruturais;
- diários quando existirem alterações;
- retenção: 10 críticos, 14 diários, 8 semanais;
- backup SQLite consistente;
- criar agora, restaurar e exportar workspace em ZIP.

Pacotes preservados:

- todas as importações;
- exportações associadas a baselines;
- exportações usadas em reimportação;
- exportações marcadas como relevantes.

## 25. Migração inicial

- Script específico para o workbook GET existente.
- Relatório de migração.
- Validação manual antes de consolidação.
- Importações futuras apenas por templates XLSX gerados pela aplicação.

## 26. Fora do MVP

- YAML e OKF;
- anexos geridos;
- leitura automática de documentos;
- LLM interna;
- geração de texto;
- geração Word;
- pesquisa semântica;
- multiutilizador;
- autenticação;
- SharePoint/cloud;
- parâmetros numéricos tipados;
- editor genérico de regras/formulários;
- importador Excel universal;
- Docker;
- aplicação desktop empacotada.
