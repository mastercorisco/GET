# GET — Plano de skills (mínimo alterações)

Documento de referência para desenvolvimento futuro. O GET mantém a arquitectura actual; as skills são agentes externos que leem contexto exportado e devolvem propostas.

## Princípios

- SQLite continua a fonte de verdade autoritativa.
- Skills **não** escrevem SQLite, **não** aprovam pontos, **não** alteram campos protegidos.
- Ciclo: **READ → REASON → PROPOSE → REVIEW → COMMIT**.
- **READ:** exportação GET-PACKAGE (bloco ou fascículo).
- **PROPOSE:** JSON devolvido → staging / `ChangeProposal`.
- **REVIEW / COMMIT:** fluxo de importação e consolidação já existente.
- Humano pode editar pontos e conhecimento directamente na app (sem obrigar proposta em cada keystroke).
- GET-LLM, Markdown, PDF e XMind são **projecções**; não são reimportáveis.

Diagrama: [GET_SKILLS_OPERATING_MODEL.drawio](GET_SKILLS_OPERATING_MODEL.drawio) (abrir em [diagrams.net](https://app.diagrams.net) ou extensão Draw.io no VS Code/Cursor).

## Skills (conjunto inicial)

| Skill | Papel | Contexto | Saídas | Proibido |
|-------|--------|----------|--------|----------|
| **get-grill** | Preparar pontos até briefing completo | Ponto, premissas herdadas, KI/refs ligados, `development_point_templates` | Patch de `title`, `core_idea`, `intended_outcome`, `lists`; candidatos glossário/ref/decisão | Marcar `ready`/`approved`; inventar requisitos sem suporte |
| **get-review** | Cross-check registado vs pontos/texto | Pacote + conhecimento, premissas, terminologia, referências | Inconsistências + propostas de correcção | Novos requisitos; promoção biblioteca; mudar approval |
| **get-decision** | Excepção: escolha transversal | Pontos afectados, decisões existentes | Propor `KnowledgeItem` `knowledge_type=decision` | Aprovar; copiar decisão para dentro de cada ponto |
| **get-research** | Excepção: fonte em falta | Afirmação + refs actuais | Propor `Reference` (+ facto opcional que cita) | Marcar verificado; converter norma em requisito |

**Não implementar agora:** get-fact-check, get-domain-model (dentro de grill/review), get-retro, get-handoff. **Geração:** exportação GET-LLM na app.

## get-grill — critério de “ponto completo”

Alinhado com validação existente (`ready` exige título, ideia central e conteúdo mínimo em listas) e com `package_guidance.py`:

- `core_idea`: afirmação técnica (não instrução de redação).
- `intended_outcome`: o que o texto final deve conseguir transmitir.
- `must_include`: obrigações verificáveis (objectos tipados, não strings soltas).
- `open_questions`: lacunas honestas com contexto para resposta humana.
- `limits_and_exclusions`, `acceptance_criteria`, `questions_to_answer`, `development_guidance` conforme o modelo do ponto.

## get-review — três comparações

1. **Registo:** afirmação ↔ premissa / facto / referência; senão → `open_questions` ou premissa `unverified` (sem scores 0–1).
2. **Decisão:** comportamento pedido ↔ decisões e premissas `mandatory`.
3. **Prática e linguagem:** glossário, exemplos vs requisitos, instruções de redação vs premissas.

## Ordem típica de uso

1. get-grill → revisão humana → aceitar propostas no GET.
2. Marcar ponto `ready` quando a validação da app permitir.
3. Export GET-LLM → redação externa.
4. get-review sobre pontos e/ou texto gerado → propostas via GET-PACKAGE.
5. get-decision / get-research apenas quando grill ou review identificarem necessidade.

## Próximo incremento de produto (opcional, pequeno)

**Decision profile v1** no perfil técnico já existente (`decision/1`), relação `applies_to`, sem MCP. Ver análise `get_framework_evolution` (conversa 2026-11-21). Adiar até sessões reais mostrarem que texto livre em decisões já não chega.

## Saídas do grill (mapeamento)

| Descoberta na interrogação | Destino na proposta |
|----------------------------|---------------------|
| Definição / termo | Candidato `TerminologyConcept` |
| Fonte documental | Candidato `Reference` |
| Facto sustentado | Candidato `KnowledgeItem` `fact` + ligação |
| Escolha de engenharia | Candidato get-decision → `KnowledgeItem` `decision` |
| Clarificação do ponto | Patch `DevelopmentPoint` |
| Relação entre itens | Candidato `KnowledgeRelation` |
| Lacuna | `open_questions` no ponto ou KI `open_question` |

## Análise de evolução do quadro

Contexto arquitectural e lacunas: [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md).

## Referências no código

- Pontos: `backend/app/domain/block/`
- GET-PACKAGE: `backend/app/services/packages/`, `schemas/get_package.schema.json`
- Orientação LLM no pacote: `backend/app/services/packages/package_guidance.py`
- Modelos de ponto: `catalogs/development_point_templates.pt-PT.json`
- Método: `docs/GET_METHOD.md`, `docs/DATA_MODEL.md`