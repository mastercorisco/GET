# GET — Evolução do quadro (resumo para desenvolvimento)

Síntese da análise *get_framework_evolution* (2026-11-21). **Não altera** ADRs nem schemas até um incremento ser aprovado explicitamente.

## Posicionamento

- GET é fonte de verdade **persistente** de conhecimento de engenharia, não apenas uma fase de workflow nem um gerador de documentos.
- IA **fora** do produto: sistema robusto que agentes podem **ler**, **questionar** e **propor** alterações via GET-PACKAGE.
- Evolução **mínima**: enriquecer o que já existe em vez de novas entidades (Jira, DOORS, grafo, memória duplicada, MCP prematuro).

## O que já cobre o modelo proposto

| Conceito proposto | Estado no GET |
|-------------------|----------------|
| Hierarquia Project / Fascicle / Block / DevelopmentPoint | Implementada (`document_node`, `development_point`) |
| Biblioteca + projecto | `KnowledgeItem` scope, `ProjectLibraryPin` |
| Glossary | `TerminologyConcept`, `ProjectTerminologyOverride` |
| Source / norma | `Reference`, `StandardProfile` |
| Decision Record (fraco) | `knowledge_type=decision` + ficha JSON livre |
| Proposta / revisão | `ChangeProposal`, import GET-PACKAGE, consolidação |
| Promoção para biblioteca | Destino `library` na `ChangeDecision` (ADR-012) |
| Geração vs roundtrip | GET-LLM (não reimportável) vs GET-PACKAGE |
| Fact-checking (categórico) | Premise `confidence`, estados de aprovação — **sem** scores 0–1 |

## Lacunas relevantes (adiáveis)

- Perfil de decisão tipado (`decision/1`) e relação `applies_to` (só `depends_on`, `related_to`, `supersedes` semeados).
- Evidência com localizador partilhado (cláusula, email) — hoje `reference_id` na premissa e refs no export.
- Revisões nos **pontos** (mutáveis; `needs_review` não é histórico).
- MCP — API HTTP já expõe leitura/escrita de pacotes; transporte futuro.

## Decisão arquitectural recomendada (OPEN até uso real)

**Decision Record = `KnowledgeItem` + perfil técnico versionado**, não entidade separada nem especialização de `DevelopmentPoint`. O ponto **cita** decisões via `knowledge_item_ids`.

`ChangeDecision` = aceitar/rejeitar importação; **não** confundir com DR de engenharia.

## Anti-objectivos

Workflow BPMN, dezenas de tabelas novas, writes automáticos de agentes, embeddings, duplicar verdade entre “memória” e SQLite, cadeia obrigatória Requirement→Deliverable→Verification.

## Skills (ver documento dedicado)

Implementação **fora** do runtime GET: [GET_SKILLS_PLAN.md](GET_SKILLS_PLAN.md) (inclui **get-orient** só leitura para ponto de situação) e diagrama [diagrams/GET_METHOD_ALL_SHEETS.drawio](diagrams/GET_METHOD_ALL_SHEETS.drawio) (metodo, 6 folhas).

## Próximo incremento de produto (quando necessário)

1. `schemas/decision-profile-1.schema.json` + validação em `technical_profile` quando `profile_schema === "decision/1"`.
2. Seed `applies_to` em `relation_type`.
3. UI de conhecimento para decisões.
4. Testes roundtrip GET-PACKAGE.

Adiar até sessões com grill/decision mostrarem que texto livre já não chega.

## Fontes de verdade (vocabulário)

| Camada | Onde |
|--------|------|
| Autoritativo | SQLite (revisões activas, pontos, terminologia, referências) |
| Evidência | `Reference`, premissa `reference_id` |
| Proposto | Staging / `ChangeProposal` |
| Gerado | GET-LLM, MD/PDF/XMind, workbook export |
| Histórico | Revisões, baselines, import/export records |

## Documentação relacionada

- [DATA_MODEL.md](DATA_MODEL.md), [GET_METHOD.md](GET_METHOD.md), [GET_APP_SPECIFICATION.md](GET_APP_SPECIFICATION.md)
- [ARCHITECTURE_DECISIONS.json](../ARCHITECTURE_DECISIONS.json)