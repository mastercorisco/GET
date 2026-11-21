# GET — Plano macro (operação e evolução)

Documento de visão para **como** usar o GET com LLMs e revisão humana, em paralelo com [`PLAN.md`](PLAN.md) (construção da aplicação, épicos E01–E08).

**Relacionados:** [GET_SKILLS_PLAN.md](GET_SKILLS_PLAN.md), [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md), [GET_SKILLS_OPERATING_MODEL.drawio](GET_SKILLS_OPERATING_MODEL.drawio), [GET_METHOD.md](GET_METHOD.md).

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
| **Agente (Cursor, Claude, …)** | READ → REASON → PROPOSE; organização opcional de ficheiros em disco; **não** escreve SQLite directamente |
| **Material de apoio** | PDF, MD, SharePoint (links); **não** fonte de verdade — só leitura para skills |

**Proveniência sem gestão de pastas na app (ADR-008):** registar origem com `Reference` (`citation`, `notes`, `internal_location` para caminho local) ou URL SharePoint em `citation`/`notes`; premissas com `reference_id`; conhecimento com `origin_context`. A organização física fica **fora** do GET.

**Development points = harness da LLM:** `core_idea`, `must_include`, `limits_and_exclusions`, `open_questions`, `reference_ids`, `llm_freedom` (por defeito `strict`) limitam a redação e reduzem invenção.

---

## 3. Fases macro (com apoio do agente)

As fases são **mapa de paragem**, não papelada. O agente ajuda a: traduzir pedidos numa única camada de mudança; pré-validar imports; manter o ritmo (export → trabalho → proposta → aceitação).

### F0 — Estrutura e importação fiáveis

**Objectivo:** Árvore documental e tipos conceptuais correctos após roundtrip; sem “baralhar” fascículo, bloco, ponto, knowledge, premissa.

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

**Skills:** [get-grill](GET_SKILLS_PLAN.md), [get-research](GET_SKILLS_PLAN.md) pontual, propostas via GET-PACKAGE.

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
| 1 | App | Export **GET-LLM** (contrato JSON, não prosa final) |
| 2 | Skill **get-write-spec** | Redige `.md` / Word **fora** do GET |
| 3 | Skill **get-review** | Cruza texto com pontos, premissas, refs, decisões |
| 4 | Engenheiro + app | Aceita correcções via GET-PACKAGE (não reimportar `.md` como verdade) |

**Saída da fase:** Texto gerado + pacote de correcções aceite; sem contradições graves com o registado.

### F3 — Conhecimento reutilizável

**Objectivo:** Deixar de repetir a mesma engenharia só dentro do texto dos pontos.

**Critérios de “feito” (exemplos):**
- Uma decisão ou premissa mandatória **citada** em mais de um contexto sem cópias contraditórias.
- Terminologia consistente (glossário usado; review sem drift).
- Norma/fonte uma vez em `Reference` (com link SharePoint ou caminho) e vários pontos com `reference_ids`.
- Promoção consciente para biblioteca (humana, ADR-012) — opcional.

**Evolução de produto opcional:** perfil `decision/1` — só quando piloto mostrar decisões mal servidas por texto livre. Ver [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md).

**Saída da fase:** “Se mudar X, sei **um** sítio no GET para actualizar e quem referencia.”

### F4 — Escala (só quando F1–F3 se repetirem)

Candidatos isolados (um de cada vez): skills Cursor versionadas; MCP só leitura/proposta; revisão versionada de pontos; UX de import melhorada. **Não** empacotar com F0–F3.

---

## 4. Macro-entregas M1 / M2 / M3 (resumo)

| ID | Nome | Prova de valor |
|----|------|----------------|
| **M1** | Bloco piloto preparado | Grill + research pontual → pontos `ready` credíveis |
| **M2** | Ciclo redação uma vez | GET-LLM → get-write-spec → get-review → GET-PACKAGE |
| **M3** | Reutilização | Conhecimento centralizado citável (refs, decisões, glossário) |

M2 **não** significa “GET escreve texto”. Significa **export JSON + skill de redação externa**.

---

## 5. Camadas (para não misturar objectivos)

Em cada sessão de trabalho, **uma camada dominante**:

1. **Estrutura** — `document_node`, ordem, títulos (F0).
2. **Harness** — `DevelopmentPoint` e listas (F1).
3. **Redação** — artefacto `.md` fora do SQLite (F2).
4. **Registo** — knowledge, refs, premissas (F1–F3).
5. **Commit** — import consolidate (sempre humano na aceitação).

O agente deve recusar pedidos do tipo “reorganiza tudo e marca ready e gera capítulo” num só passo.

---

## 6. Melhorias de importação (backlog macro)

Derivado de experiência real (reestruturação na LLM + import problemático):

| Prioridade | Item | Tipo |
|------------|------|------|
| Alta | Ritual + checklist pré-import (agente) | Processo |
| Alta | Um âmbito de mudança por ficheiro devolvido | Processo |
| Média | Relatório “conceitos misturados” no staging | Produto — **v1:** `conceptual_warnings` na resposta de import + script F0 |
| Média | Identidade pacote vs árvore (`block_id`, `display_code`, `structure_anchor`) | Produto — **feito Onda 1** |
| Média | `export_record` por projecto (não `export_id` global) | Produto — **feito** (migração 010) |
| Média | UI de aceitação por grupo (pontos / premissas / knowledge) | Produto |
| Baixa | Modos de import (estrutura vs conteúdo) | Produto |

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
- MCP, grafo de conhecimento ou dezenas de tabelas antes de F2 provado.

---

## 9. Estado e revisão

| Campo | Valor |
|--------|--------|
| Versão documento | 1.0.1 |
| Última actualização | 2026-11-21 |
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

Actualizar este ficheiro quando fechares F0, M1, M2 ou M3, ou quando o backlog da secção 6 mudar de prioridade.