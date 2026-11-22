# GET — Plano macro (operação e evolução)

Documento de visão para **como** usar o GET com LLMs e revisão humana, em paralelo com [`PLAN.md`](PLAN.md) (construção da aplicação, épicos E01–E08).

**Relacionados:** [GET_SKILLS_PLAN.md](GET_SKILLS_PLAN.md), [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md), [diagrams/GET_METHOD_ALL_SHEETS.drawio](diagrams/GET_METHOD_ALL_SHEETS.drawio), [GET_METHOD.md](GET_METHOD.md).

---

## 1. Dois planos

| Plano | Pergunta | Onde |
|--------|----------|------|
| **Produto** | O que falta implementar na app? | `PLAN.md` |
| **Macro (este documento)** | Como ganhar valor de engenharia e caderno com o que já existe? | Fases, rituais, skills, melhorias de import |

O GET **não redige** o caderno. A app exporta contratos (GET-PACKAGE, GET-LLM); agentes externos propõem alterações; o engenheiro **commita** no SQLite.

---

## 2. Papéis

| Papel | Responsabilidade |
|--------|------------------|
| **Engenheiro** | Autoridade técnica; aceitar/rejeitar propostas; marcar `ready` / `approved` nos pontos; baseline |
| **GET (app)** | Fonte de verdade; validação determinística; export/import roundtrip |
| **Agente (Cursor, Claude, …)** | READ → REASON → PROPOSE (ou **só ANSWER** em get-orient); organização opcional de ficheiros em disco; **não** escreve SQLite directamente |
| **Material de apoio** | PDF, MD, SharePoint (links); **não** fonte de verdade — só leitura para skills |

**Proveniência sem gestão de pastas na app (ADR-008):** registar origem com `Reference` (`citation`, `notes`, `internal_location` para caminho local) ou URL SharePoint em `citation`/`notes`; premissas com `reference_id`; conhecimento com `origin_context`. A organização física fica **fora** do GET.

**Development points = harness da LLM:** `core_idea`, `must_include`, `limits_and_exclusions`, `open_questions`, `reference_ids`, `llm_freedom` (por defeito `strict`) limitam a redação e reduzem invenção.

### 2.1 Terminologia — duas camadas

| Camada | Fonte | Uso na redação |
|--------|--------|----------------|
| **Léxico estrutural** | Catálogo `document_lexicon.text_production.pt-PT.json` | Rótulos capítulo/ponto nos MD GET-LLM (ADR-057) |
| **Glossário técnico** | SQLite `terminology_concept` (biblioteca + projecto) e `project_terminology_override` | Vocabulário vinculativo para caderno e revisão linguística |

**Regra macro:** na fase **F2**, a redação externa deve ler o **glossário técnico exportado** (`terminology_{profile}_llm.md` no ZIP GET-LLM). Termos novos vindos de normas ou corpus entram via **registo (F1/F3)** ou futura skill **get-lexicon**; o texto redigido **não** é fonte de verdade para o léxico.

---

## 3. Fases macro (com apoio do agente)

As fases são **mapa de paragem**, não papelada. O agente ajuda a: traduzir pedidos numa única camada de mudança; pré-validar imports; manter o ritmo (export → trabalho → proposta → aceitação).

### F0 — Estrutura e importação fiáveis

**Objectivo:** Árvore documental e tipos conceptuais correctos após roundtrip; sem “baralhar” fascículo, bloco, ponto, knowledge, premissa.

**Orientação:** após consolidate ou quando o estado no disco/UI estiver confuso, sessão **get-orient** (só leitura): export GET-LLM mestre + manifest, ou GET-PACKAGE do fascículo afectado — **sem** nova proposta na mesma conversa. Ver [GET_SKILLS_PLAN.md](GET_SKILLS_PLAN.md#get-orient--ponto-de-situação-só-leitura).

**Problemas a atacar (prioridade alta):**
- Reorganização feita na LLM num único ficheiro → import conceptualmente sujo.
- Aceitação de propostas pouco amigável para grandes volumes.

**Ritual seguro (já aplicável):**
1. Um **tipo de mudança** por ciclo: só estrutura (nós/ordem/títulos) *ou* só conteúdo de bloco *ou* só knowledge — nunca “reorganização total”.
2. Export canónico (GET-PACKAGE alinhado ao baseline quando aplicável).
3. Agente: checklist pré-import (tipos misturados, decisões dentro de pontos, etc.).
4. Import → revisão por grupos → consolidate.

**Evolução de produto (quando F0 voltar a doer):** relatório semântico no dry-run; aceitação agrupada na UI; modos explícitos de import.

**Saída da fase:** Um fascículo ou subárvore estável; importação sem corrupção conceptual.

### F1 — Bloco piloto preparado (harness)

**Objectivo:** Pontos informativos e completos para redação de qualidade.

**Skills:** [get-orient](GET_SKILLS_PLAN.md) (ponto de situação, antes do piloto), [get-grill](GET_SKILLS_PLAN.md), [get-research](GET_SKILLS_PLAN.md) pontual, propostas via GET-PACKAGE.

**Terminologia:** grill/research podem propor **candidatos** `TerminologyConcept`; commit na app ou (futuro) via MCP com **confirmação explícita** do utilizador — não bloqueia o piloto F1.

**Modo “grill me”:** diálogo para confirmar ideias **antes** de as incluir na proposta; a skill devolve conteúdo estruturado, não autoridade.

**Estado `ready`:**
- Critério de **grill**: checklist alinhado à validação da app (título, ideia central, listas mínimas).
- **Marcação `ready`:** preferencialmente **humana** na UI (ou após validação determinística passar).
- Na consolidação de **updates** de ponto, `status` **não** é aplicado a partir do pacote — só campos editáveis (`core_idea`, `lists`, …). Evita a LLM “promover” pontos sem controlo.

**Saída da fase:** ≥1 bloco com pontos `ready`; referências com links/caminhos onde aplicável.

### F2 — Ciclo completo de redação (uma vez)

**Objectivo:** Provar M2 de ponta a ponta **sem** o GET produzir texto.

| Passo | Quem | O quê |
|-------|------|--------|
| 1 | App | Export **GET-LLM** (contrato JSON + MD derivado), incluindo **`terminology_{profile}_llm.md`** no ZIP e referência no `master_*_llm.md` |
| 2 | Skill **get-write-spec** | Redige `.md` / Word **fora** do GET; glossário técnico = lista **obrigatória** (preferencial, evitar, overrides) |
| 3 | Skill **get-review** | Cruza texto com pontos, premissas, refs, decisões e **glossário exportado** |
| 4 | Engenheiro + app | Aceita correcções via GET-PACKAGE (não reimportar `.md` como verdade) |

**Saída da fase:** Texto gerado + pacote de correcções aceite; sem contradições graves com o registado.

**Iteração de produto (glossário no pacote):** ver [micro-F2-terminology-llm-export.md](plans/micro-F2-terminology-llm-export.md) (ADR-061).

### F3 — Conhecimento reutilizável

**Objectivo:** Deixar de repetir a mesma engenharia só dentro do texto dos pontos.

**Critérios de “feito” (exemplos):**
- Uma decisão ou premissa mandatória **citada** em mais de um contexto sem cópias contraditórias.
- **Terminologia consistente:** glossário populado no GET; export GET-LLM inclui `terminology_*_llm.md`; get-review sem drift vs `avoid_terms` / overrides.
- Norma/fonte uma vez em `Reference` (com link SharePoint ou caminho) e vários pontos com `reference_ids`.
- Promoção consciente para biblioteca (humana, ADR-012) — opcional.

**Evolução de produto opcional:** perfil `decision/1` — só quando piloto mostrar decisões mal servidas por texto livre. Ver [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md).

**Saída da fase:** “Se mudar X, sei **um** sítio no GET para actualizar e quem referencia.”

### F4 — Escala (só quando F1–F3 se repetirem)

Candidatos **isolados** (um de cada vez): skills Cursor versionadas; **servidor MCP local** (ver §3.2); revisão versionada de pontos; UX de import melhorada. **Não** empacotar implementação MCP completa com F0–F3, mas **preparação API** (leitura, search) pode anteceder F2.

### 3.2 MCP local e gestão de léxico

| Princípio | Regra |
|-----------|--------|
| Transporte | MCP em `127.0.0.1`; chama **API FastAPI**; **nunca** SQLite directo |
| Leitura | list, get, snapshot do export, search — sem confirmação |
| Escrita | `POST` / `PATCH` / `DELETE` só após **confirmação explícita** do utilizador (conversa + parâmetro `confirm` na API onde aplicável; precedente: restauro de backup) |
| Skills | READ → PROPOSE JSON; MCP opcional para commit confirmado |

**Ondas:**

| Onda | Quando | Entrega |
|------|--------|---------|
| **T0** | Iteração glossário no ZIP | `terminology_{profile}_llm.md` no pacote GET-LLM (produto app) |
| **T1** | M2 em curso | `GET /api/terminology/search`; skill **get-lexicon** (READ + PROPOSE) |
| **T2** | F4 | Servidor MCP: tools leitura + search + mutações com confirmação → API existente |
| **T3** | F4+ | Propostas tipadas (staging) antes de commit; alinhado a GET-PACKAGE onde couber |

---

## 4. Macro-entregas M1 / M2 / M3 (resumo)

| ID | Nome | Prova de valor |
|----|------|----------------|
| **M0** *(transversal)* | Ponto de situação legível | get-orient sobre mestre/índice → foco F0/F1 escolhido com evidência no export |
| **M1** | Bloco piloto preparado | Grill + research pontual → pontos `ready` credíveis |
| **M2** | Ciclo redação uma vez | GET-LLM (com glossário `.md`) → get-write-spec → get-review → GET-PACKAGE |
| **M3** | Reutilização | Conhecimento centralizado citável (refs, decisões, glossário) |

M2 **não** significa “GET escreve texto”. Significa **export JSON/MD + skill de redação externa**.

---

## 5. Camadas (para não misturar objectivos)

Em cada sessão de trabalho, **uma camada dominante**:

1. **Estrutura** — `document_node`, ordem, títulos (F0).
2. **Harness** — `DevelopmentPoint` e listas (F1).
3. **Redação** — artefacto `.md` fora do SQLite (F2).
4. **Registo** — knowledge, refs, premissas, **terminologia** (F1–F3).
5. **Commit** — import consolidate (sempre humano na aceitação).

O agente deve recusar pedidos do tipo “reorganiza tudo e marca ready e gera capítulo” num só passo.

---

## 6. Melhorias de importação (backlog macro)

Derivado de experiência real (reestruturação na LLM + import problemático):

| Prioridade | Item | Tipo |
|------------|------|------|
| Alta | Ritual + checklist pré-import (agente) | Processo |
| Alta | Um âmbito de mudança por ficheiro devolvido | Processo |
| **Alta** | Glossário E05 em `terminology_*_llm.md` no ZIP GET-LLM | Produto — **T0 / ver micro-F2** |
| Média | Relatório “conceitos misturados” no staging | Produto — **v1:** `conceptual_warnings` na resposta de import + script F0 |
| Média | Identidade pacote vs árvore (`block_id`, `display_code`, `structure_anchor`) | Produto — **feito Onda 1** |
| Média | `export_record` por projecto (não `export_id` global) | Produto — **feito** (migração 010) |
| Média | UI de aceitação por grupo (pontos / premissas / knowledge) | Produto |
| Média | `GET /api/terminology/search` | Produto — **T1 feito** (ADR-062) |
| Média | `confirm` em DELETE terminologia | Produto — T2 |
| Baixa | Modos de import (estrutura vs conteúdo) | Produto |
| Baixa | MCP stdio local + tools | Infra — T2–T3 |
| Baixa | Skill get-lexicon versionada | Processo — T1 |

**Nota técnica actual:** merge de bloco não propaga `status` em `point_update` — por desenho. Qualquer mudança para “propor ready via pacote” exige proposta explícita, validação e UX dedicada (não silenciosa).

---

## 7. Planos micro (como derivar)

Após cada fase ou a cada piloto concluído:

1. **Retro** — O que ficou só no chat ou no disco e devia estar no GET?
2. **Decisão** — Uma questão OPEN resolvida ou adiada com motivo.
3. **Plano micro** (1–3 páginas) — âmbito, ficheiros, fora de âmbito, critérios de aceitação.
4. **Experimento único** — um bloco, um import, uma skill.

Modelo de título: `docs/plans/micro-F1-bloco-XX-grill.md` (criar quando necessário; não obrigatório no MVP).

---

## 8. Anti-objectivos (macro)

- GET como gerador autónomo de texto ou Word canónico.
- Gestão de corpus / pastas dentro da app.
- Import “tudo em um” da LLM sem revisão conceptual.
- `ready` / `approved` automáticos pela skill sem validação humana ou regras da app.
- **Servidor MCP com escrita** antes de F2 provado (export glossário no ZIP **é** produto F2, não MCP).
- Agentes ou MCP com acesso **directo** ao ficheiro SQLite.
- MD redigido fora do GET reimportado como verdade canónica.

---

## 9. Estado e revisão

| Campo | Valor |
|--------|--------|
| Versão documento | 1.1.0 |
| Última actualização | 2026-11-22 |
| **Fase macro activa** | **F0 — em curso** |
| Entregáveis F0 | [docs/plans/](plans/README.md) |
| Próxima revisão sugerida | Após piloto F0-structure + retro; depois F1 |

### F0 — progresso

| Passo | Estado |
|-------|--------|
| Ritual + checklist + Phase A inventory | Documentado |
| Phase A inventário incidente (canal) | **Feito** — [micro-F0-phase-A-workspace-testes.md](plans/micro-F0-phase-A-workspace-testes.md) |
| Piloto roundtrip F0-structure | **Pendente** (humano + workspace) |
| Retro + fecho F0 | Template pronto |

### F1 — bloco piloto (preparação)

| Passo | Estado |
|-------|--------|
| Skill **get-grill** (Cursor) | **Feito** (`agent-skills/get-grill`; piloto bloco pendente) |
| Skill **get-research** (Cursor) | **Feito** (`agent-skills/get-research`) |
| Piloto M1 (≥1 bloco, pontos `ready`) | **Pendente** — [micro-F1-bloco-piloto-grill.md](plans/micro-F1-bloco-piloto-grill.md) |

### Transversal — glossário no pacote GET-LLM (F2 / T0)

| Passo | Estado |
|-------|--------|
| Plano macro + micro-F2 | **Feito** |
| Implementação `terminology_*_llm.md` no ZIP | **Feito** (ADR-061; ver micro-F2) |
| JSON `terminology_*_llm.json` no ZIP | **Feito** (GET-LLM-TERMINOLOGY) |

### F2 — ciclo redação (M2)

| Passo | Estado |
|-------|--------|
| Export GET-LLM + glossário (app) | **Feito** (T0) |
| Skill **get-write-spec** | **Feito** (`agent-skills/get-write-spec`) |
| Skill **get-review** | **Feito** (`agent-skills/get-review`) |
| Piloto M2 ponta a ponta | **Pendente** (texto + review + import) |

### F3 — reutilização (preparação)

| Passo | Estado |
|-------|--------|
| Skill **get-decision** (Cursor) | **Feito** (`agent-skills/get-decision`) |
| Piloto decisão citada em ≥2 contextos | **Pendente** (humano) |

### Conjunto skills Cursor (inicial)

| Passo | Estado |
|-------|--------|
| 7 skills em `agent-skills/` | **Feito** (MANIFEST 1.2.0) |
| Pilotos M0–M3 | **Pendente** (sessões com workspace CTBJ) |

### T1 — pesquisa de glossário

| Passo | Estado |
|-------|--------|
| `GET /api/terminology/search` | **Feito** (ADR-062; [micro-T1-terminology-search.md](plans/micro-T1-terminology-search.md)) |
| Skill get-lexicon (Cursor) | **Feito** (`agent-skills/get-lexicon`; piloto humano pendente) |

### T2 — MCP local (F4)

| Passo | Estado |
|-------|--------|
| ADR-063 + catálogo tools + micro-plano | **Feito** — [micro-T2-mcp-get-server.md](plans/micro-T2-mcp-get-server.md), [mcp/TOOL_CATALOG.md](mcp/TOOL_CATALOG.md) |
| Implementação `mcp-get/` (stdio + proxy HTTP) | **Adiado** até fecho **M2** (checklist no micro-plano) |
| Tools de escrita com `confirm` | **T2.1** — após T2.0 leitura |

Actualizar este ficheiro quando fechares F0, M1, M2 ou M3, ou quando o backlog da secção 6 mudar de prioridade.