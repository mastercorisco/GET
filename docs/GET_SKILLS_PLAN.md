# GET — Plano de skills (mínimo alterações)

Documento de referência para desenvolvimento futuro. O GET mantém a arquitectura actual; as skills são agentes externos (ex.: Cursor, Claude) que leem contexto exportado, eventual **corpus de apoio** em disco, e devolvem propostas.

## Princípios

- **Fonte de verdade:** SQLite (conhecimento aceite, pontos, referências como registos).
- **Material de apoio:** pastas com Markdown, PDFs, normas — leitura para LLMs; **não** fonte de verdade. O que importa para engenharia ou caderno entra no GET após revisão (`Reference` com `internal_location`, factos, premissas, pontos).
- **Memória de sessão** (ex. Claude): cache de trabalho; não substitui GET nem o corpus indexado em disco.
- Skills **não** escrevem SQLite, **não** aprovam pontos, **não** alteram campos protegidos.
- Ciclo: **READ → REASON → PROPOSE → REVIEW → COMMIT**.
- **READ:** exportação GET-PACKAGE (bloco ou fascículo) +, quando útil, ficheiros em `corpus/` (ver abaixo).
- **PROPOSE:** JSON devolvido → staging / `ChangeProposal`.
- **REVIEW / COMMIT:** fluxo de importação e consolidação já existente.
- Humano pode editar pontos e conhecimento directamente na app (sem obrigar proposta em cada keystroke).
- Exportações na app (GET-LLM, Markdown, PDF, XMind) são **projecções / contratos**; não produzem o texto final do caderno e não são reimportáveis como autoridade (excepto GET-PACKAGE).

Diagrama do método ([draw.io](https://app.diagrams.net)): [diagrams/GET_METHOD_ALL_SHEETS.drawio](diagrams/GET_METHOD_ALL_SHEETS.drawio) (6 folhas).

## Corpus de apoio (LLMs)

Fora do SQLite (ADR-008: a app não armazena anexos). Convenção recomendada por projecto:

```text
{raiz do workspace ou projecto}/
  corpus/
    manifest.json ou _index.md   # inventário, datas, aplicabilidade
    norms/                     # normas PDF (+ resumo .md opcional)
    client/                    # RCD, atas, emails exportados
    site/                      # as-built, levantamentos
    vendor/                    # datasheets
    engineering/               # notas MD internas (não duplicar biblioteca GET)
  exports/                     # artefactos GET (já existente)
```

- Cada documento importante deve ter (ou vir a ter) um registo **`Reference`** / **`StandardProfile`** no GET, com **`internal_location`** apontando para o ficheiro.
- O GET-PACKAGE **não inclui** binários; skills com acesso ao disco leem o corpus; opcionalmente `project.llm_context_json` indica a raiz do corpus e regras de uso.
- Resumos `.md` de PDFs grandes reduzem tokens; o PDF permanece evidência citável.

## Skills (conjunto inicial)

| Skill | Papel | Contexto | Saídas | Proibido |
|-------|--------|----------|--------|----------|
| **get-orient** | **Leitura / ponto de situação** (projecto, fascículo, biblioteca) | GET-LLM mestre + `manifest` do ZIP; índice fascículo; GET-PACKAGE de amostra; `GET /api/knowledge/search`; workbook export (contagens); corpus se indicado em `llm_context_json` | Respostas em prosa + listas (lacunas, riscos, focos sugeridos); opcionalmente “próxima sessão: grill bloco X” | GET-PACKAGE ou alterações ao registado; marcar estados; inventar factos; substituir pesquisa FTS para citações exatas |
| **get-grill** | Preparar pontos até briefing completo | GET-PACKAGE, premissas herdadas, KI/refs ligados, `development_point_templates`, corpus | Patch de `title`, `core_idea`, `intended_outcome`, `lists`; candidatos glossário/ref/decisão; pedidos a research | Marcar `ready`/`approved`; inventar requisitos sem suporte |
| **get-research** | Apoio na preparação do bloco: encontrar norma, fabricante, prática | Lacuna concreta (grill/review), corpus, web se aplicável, refs GET actuais | Propor `Reference` + `internal_location`; resumo MD no corpus; `fact` opcional que cita a ref | Marcar verificado; converter norma em requisito; correr em todos os pontos sem gatilho |
| **get-write-spec** | **Redação** do texto da especificação (LLM externa) | Export GET-LLM (JSON + MD derivado), regras de geração, pontos `ready`/`approved` | Markdown (ou Word noutra ferramenta); **não** commit no GET | Alterar SQLite; aprovar conteúdo; reimportar MD como verdade |
| **get-review** | Cross-check registado vs pontos vs texto redigido | Pacote + conhecimento, premissas, terminologia, referências, texto `get-write-spec` | Inconsistências + propostas de correcção | Novos requisitos; promoção biblioteca; mudar approval |
| **get-decision** | Excepção: escolha transversal | Pontos afectados, decisões existentes | Propor `KnowledgeItem` `knowledge_type=decision` | Aprovar; copiar decisão para dentro de cada ponto |

**Na app (não é skill):** export GET-LLM / estrutura documental — **contrato** para `get-write-spec`.

**Não implementar agora:** get-fact-check, get-domain-model (dentro de grill/review), get-retro, get-handoff.

**Prioridade de documentação / skill Cursor:** `get-orient` (só leitura) **antes** do piloto F1 em [`micro-F1-bloco-piloto-grill.md`](plans/micro-F1-bloco-piloto-grill.md); ver [`plans/micro-get-orient-skill.md`](plans/micro-get-orient-skill.md).

## get-orient — ponto de situação (só leitura)

**Problema:** O engenheiro precisa de perguntar “onde estamos?” (estrutura, harness, biblioteca, imports pendentes) **sem** abrir um ciclo de proposta nem misturar com grill ou redação.

**Ciclo:** READ → REASON → **ANSWER** (não PROPOSE por defeito).

### Entradas recomendadas (por profundidade)

| Nível | Artefacto | Uso |
|-------|-----------|-----|
| Panorama | GET-LLM `project_master` + `manifest.json` do ZIP | Mapa fascículos/blocos; quais exports existem |
| Fascículo | GET-LLM fascículo-índice ou GET-PACKAGE fascículo (se estrutura recente) | Ordem, títulos, KI editáveis |
| Bloco | GET-PACKAGE bloco exportado | Detalhe de pontos, premissas, `open_questions` |
| Biblioteca | Pesquisa FTS na app + KI no mestre / pins do projecto | Termos, decisões, factos reutilizáveis |
| Métricas | Workbook projecto (Excel derivado) | Contagens por `status`, rascunhos — **não** fonte de verdade, só apoio |

### Perguntas típicas

- Que fascículos/blocos têm mais pontos `draft` / `incomplete`?
- Que `open_questions` se repetem ou bloqueiam F2?
- Que refs biblioteca ou decisões já cobrem este tema?
- O último import deste fascículo foi estrutural ou conteúdo? (correlacionar com ritual F0)
- O que falta antes de marcar um bloco piloto para grill?

### Saídas permitidas

- Narrativa estruturada (estado, riscos, dependências).
- Lista priorizada de **próximos trabalhos** (ex.: “sessão grill F04_B07”; “research norma Y”).
- Perguntas de clarificação ao engenheiro.

### Saídas proibidas (sem pedido explícito separado)

- Ficheiro GET-PACKAGE devolvido como “resposta”.
- Afirmações de contagem ou UUID **sem** base no export/pesquisa fornecidos — dizer “não consta no contexto fornecido”.
- Consolidar ou assumir que staging foi aceite.

### Relação com outras skills

| Situação | Skill |
|----------|--------|
| Perceber estado global ou local | **get-orient** |
| Melhorar pontos com proposta JSON | **get-grill** (+ **get-research**) |
| Redigir texto do caderno | **get-write-spec** (após pontos `ready`) |
| Texto já redigido vs registado | **get-review** |

Se durante **get-orient** surgir trabalho claro num bloco, **terminar** a sessão de orientação e abrir **nova** sessão get-grill com GET-PACKAGE desse bloco.

### Complemento produto (roadmap, não skill)

Relatório determinístico na app (contagens, staging, `needs_review`) reduz alucinação em métricas; a skill mantém-se útil para síntese e priorização. Ver [GET_MACRO_PLAN.md](GET_MACRO_PLAN.md) §6.

## get-grill — critério de “ponto completo”

Alinhado com validação existente (`ready` exige título, ideia central e conteúdo mínimo em listas) e com `package_guidance.py`:

- `core_idea`: afirmação técnica (não instrução de redação).
- `intended_outcome`: o que o texto final deve conseguir transmitir.
- `must_include`: obrigações verificáveis (objectos tipados, não strings soltas).
- `open_questions`: lacunas honestas com contexto para resposta humana.
- `limits_and_exclusions`, `acceptance_criteria`, `questions_to_answer`, `development_guidance` conforme o modelo do ponto.

Quando uma lacuna depende de documentação externa, o grill **sinaliza** (ex. `open_questions` ou encaminha **get-research**) em vez de inventar conteúdo.

## get-research — gatilhos e limites

Usar quando houver:

- premissa ou afirmação `unverified` que exige norma, datasheet ou documento de cliente;
- `open_questions` do grill com fonte identificável;
- `must_include` que depende de cláusula ou capacidade de equipamento documentada.

Evitar: pesquisa genérica “sobre o assunto” em todos os pontos do bloco (ruído e refs duplicadas). Consolidar no GET só após aceitar propostas no import.

## get-write-spec — redação

- Lê o pacote GET-LLM (preparação, premissas, `llm_freedom`, listas dos pontos).
- Desenvolve texto respeitando limites e separando sugestões não aprovadas (modo `exploratory` nos pontos).
- O resultado é **artefacto de leitura**; conhecimento novo volta via **get-review** + GET-PACKAGE, não por colar Markdown na app.

## get-review — três comparações

1. **Registo:** afirmação ↔ premissa / facto / referência / corpus citado; senão → `open_questions` ou premissa `unverified` (sem scores 0–1).
2. **Decisão:** comportamento pedido ↔ decisões e premissas `mandatory`.
3. **Prática e linguagem:** glossário, exemplos vs requisitos, instruções de redação vs premissas.

## Ordem típica de uso

0. **get-orient** (opcional, recomendado no arranque de fase ou após import grande) → escolher âmbito da próxima sessão.
1. **get-grill** (+ **get-research** quando houver lacuna documental) → revisão humana → aceitar propostas no GET.
2. Marcar ponto **`ready`** quando a validação da app permitir; registar refs com `internal_location` no corpus quando aplicável.
3. Export **GET-LLM** → **get-write-spec** (redação).
4. **get-review** sobre pontos e texto redigido → propostas via GET-PACKAGE.
5. **get-decision** quando grill ou review identificarem escolha transversal ainda por documentar.

## Saídas do grill (mapeamento)

| Descoberta na interrogação | Destino na proposta |
|----------------------------|---------------------|
| Definição / termo | Candidato `TerminologyConcept` |
| Fonte documental | Candidato `Reference` (+ path no corpus) |
| Facto sustentado | Candidato `KnowledgeItem` `fact` + ligação |
| Escolha de engenharia | Candidato get-decision → `KnowledgeItem` `decision` |
| Clarificação do ponto | Patch `DevelopmentPoint` |
| Relação entre itens | Candidato `KnowledgeRelation` |
| Lacuna | `open_questions` no ponto, research, ou KI `open_question` |

## Próximo incremento de produto (opcional, pequeno)

**Decision profile v1** no perfil técnico já existente (`decision/1`), relação `applies_to`, sem MCP. Ver [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md). Adiar até sessões reais mostrarem que texto livre em decisões já não chega.

**Corpus:** pode documentar-se só no disco + manifest; evolução futura opcional: campo em `llm_context_json` com path canónico do corpus (sem alterar ADR-008).

## Plano macro

Fases de operação (F0 import → F3 reutilização): [GET_MACRO_PLAN.md](GET_MACRO_PLAN.md).

## Análise de evolução do quadro

Contexto arquitectural e lacunas: [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md).

## Referências no código

- Pontos: `backend/app/domain/block/`
- GET-PACKAGE: `backend/app/services/packages/`, `schemas/get_package.schema.json`
- GET-LLM: `backend/app/services/llm_export/`
- Orientação LLM no pacote: `backend/app/services/packages/package_guidance.py`
- Referências: `backend/app/models/reference.py` (`internal_location`)
- Contexto projecto LLM: `project.llm_context_json` em `backend/app/models/project.py`
- Modelos de ponto: `catalogs/development_point_templates.pt-PT.json`
- Método: [GET_METHOD.md](GET_METHOD.md), [DATA_MODEL.md](DATA_MODEL.md)