# F0 — Ritual de importação (uma camada por ciclo)

Versão: 1.0.0 · Fase macro: [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) F0.

## Objetivo

Evitar baralhar **estrutura documental**, **pontos**, **premissas** e **conhecimento** (`KnowledgeItem`) num único ciclo LLM → import.

## Regra de ouro

**Um ficheiro devolvido = uma camada dominante.** Ciclos separados no tempo (dias ou sessões distintas).

| Camada | Modo F0 | Âmbito GET-PACKAGE |
|--------|---------|-------------------|
| Estrutura | `F0-structure` | Fascículo (nós, ordem, títulos de blocos) |
| Harness / conteúdo | `F0-content-block` | Bloco (pontos, premissas do bloco) |
| Conhecimento transversal | `F0-knowledge` | Fascículo (`editable_knowledge` apenas) |

## Modos — permitido / proibido

### F0-structure (fascículo)

| Permitido | Proibido |
|-----------|----------|
| Títulos e ordem de `document_node` (blocos) dentro do fascículo exportado | Alterar `development_points` |
| Ajustes de `sort_key` / ordem relativa se o schema do export o suportar | `editable_knowledge.*` |
| | Novos KI, premissas, pontos |

### F0-content-block (bloco)

| Permitido | Proibido |
|-----------|----------|
| `development_points`: `title`, `core_idea`, `intended_outcome`, `lists` (objectos tipados) | Estrutura fora do bloco |
| `premises` do bloco | `editable_knowledge` do fascículo |
| | Marcar `status` como `ready`/`approved` esperando que o import aplique (updates não propagam `status`) |
| | Strings nuas em `must_include`, `open_questions`, etc. |

### F0-knowledge (fascículo)

| Permitido | Proibido |
|-----------|----------|
| `editable_knowledge` com KI schema-completos (`knowledge_type`, `states`, `provenance`, …) | Copiar `protected_context` para `editable` como atalho |
| Decisões, open_questions, facts no bucket correcto | Editar pontos em blocos |
| | Reorganizar árvore documental |

Referência anti-padrões: `backend/app/services/packages/package_guidance.py` → `PACKAGE_ANTI_PATTERNS`.

## Fluxo operacional (UI)

```text
Backup crítico
    ↓
Export GET-PACKAGE (bloco ou fascículo) — guardar ficheiro + export_id
    ↓
LLM com modo F0-* (prompt abaixo) + llm_brief da exportação
    ↓
Checklist pré-import (humano + agente)
    ↓
Validação offline (a partir de `backend/`, com venv activo):

```powershell
python scripts/validate_get_package_file.py <caminho\ficheiro.json> --project-id <project-uuid>
```

O script corre validação estrita (`validate_get_package`) e avisos conceptuais heurísticos F0.
    ↓
POST import (Reimportar / packages/import) → merge
    ↓
Rever propostas por grupo (estrutura | pontos | premissas | knowledge)
    ↓
Consolidate (sem batch se houver conflitos)
    ↓
Re-export e verificação visual na árvore / bloco
```

APIs (referência):

- Pacote bloco/fascículo: `POST /api/projects/{id}/packages/import`
- Fascículo legado: `POST /api/projects/{id}/imports`
- Consolidar pacote: `POST /api/projects/{id}/packages/merge/{merge_id}/consolidate`

Ver exclusividade workspace: [WORKSPACE_OPERATIONS.md](../WORKSPACE_OPERATIONS.md).

## Prompts LLM (copiar e adaptar)

### Cabeçalho comum (todas as sessões)

```text
Trabalhas sobre um GET-PACKAGE 1.0.0 já exportado.
- Devolves APENAS o JSON completo do envelope (sem prose).
- rules, rules_hash, schema, schema_version, scope, export_id: byte-a-byte iguais ao ficheiro recebido.
- Não omitas entidades existentes (omissão NÃO é eliminação).
- Novos IDs só new_001, new_002, …
- Listas de pontos: sempre objectos tipados, nunca strings soltas.
```

### F0-structure

```text
MODO: F0-structure
Só podes alterar estrutura documental do fascículo exportado (títulos/ordem de blocos).
NÃO alteres development_points, premises, editable_knowledge, protected_context.
```

### F0-content-block

```text
MODO: F0-content-block
Só podes alterar o bloco exportado: objective, scope, development_points, premises desse bloco.
NÃO alteres editable_knowledge do fascículo nem estrutura fora do bloco.
NÃO inventes valores numéricos ou requisitos normativos sem base no pacote — usa open_questions.
```

### F0-knowledge

```text
MODO: F0-knowledge
Só podes alterar payload.editable_knowledge.* com knowledge items completos (schema).
NÃO alteres pontos de desenvolvimento nem árvore documental.
Decisões em knowledge_type=decision; lacunas em open_question; não metas decisões no core_idea de pontos.
```

## Checklist pré-import

Marcar antes de upload:

- [ ] Modo F0-* declarado na sessão LLM e reflectido no diff esperado
- [ ] `rules_hash` inalterado face ao export original
- [ ] `scope.project_id` (e `block_id` / `fascicle_id`) correctos
- [ ] Sem mistura: decisões em KI, não em pontos
- [ ] Listas de pontos sem strings nuas
- [ ] Número de alterações compatível com o modo (alerta se >30 propostas num “teste de humo”)
- [ ] Backup criado após último consolidate bom
- [ ] Validador CLI executado sem erro (avisos conceptuais lidos)

## Aceitação na UI (user-friendly)

1. Abrir ecrã **Reimportar** após merge.
2. Ordenar mentalmente por `proposal_kind` (quando visível) ou por título da proposta.
3. **Aceitar em lotes:** primeiro só estrutura; depois pontos; depois knowledge.
4. Evitar **aceitar tudo em lote** se a lista de conflitos não estiver vazia.
5. Após consolidate, rever **árvore documental** e um bloco amostra antes de novo export LLM.

Melhorias de UI (filtro por grupo) = backlog F0-spike; ver macro plan secção 6.

## Piloto mínimo (Phase C)

1. Escolher fascículo (registar código F0x no [retro](micro-F0-retro-TEMPLATE.md)).
2. Modo **F0-structure** — alteração mínima (ex.: corrigir 1 título).
3. Roundtrip completo.
4. Só depois, noutra sessão: **F0-content-block** ou **F0-knowledge**.

## Fecho F0

- Preencher retro a partir do template.
- Actualizar tabela em [README.md](README.md) e secção 9 de [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md).
- Se piloto falhar outra vez → planear `micro-F0-import-ux-spike`. Senão → `micro-F1-bloco-piloto-grill.md`.