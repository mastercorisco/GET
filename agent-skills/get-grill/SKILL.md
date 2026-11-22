---
name: get-grill
description: Prepara pontos de desenvolvimento com GET-PACKAGE por bloco; PROPOSE campos editáveis sem marcar ready.
disable-model-invocation: true
---

# get-grill — preparar harness do bloco (READ → PROPOSE)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (get-grill). Piloto activo: `docs/plans/micro-F1-bloco-F04_B07-grill.md` · prompt: `docs/plans/micro-F1-grill-session-prompt.md`.

## Modo

- Ciclo: **READ → REASON → PROPOSE** (devolver GET-PACKAGE ou patch JSON validável).
- **Grill me:** confirmar ideias com o engenheiro antes de incluir na proposta.
- Sessão dedicada: não misturar com get-write-spec nem reorganização estrutural global (F0).

## Contexto mínimo

1. GET-PACKAGE exportado do bloco (`scope_kind: block`) — JSON canónico actual da app.
2. Opcional: fascículo/bloco código (`display_code`), `project_id`.
3. Corpus em disco apenas como apoio; premissas/refs finais entram no pacote proposto.
4. Terminar sessão **get-orient** antes de abrir get-grill no mesmo bloco.

## Campos a enriquecer (editáveis)

Por ponto: `title`, `core_idea`, `intended_outcome`, listas (`must_include`, `limits_and_exclusions`, `open_questions`, `acceptance_criteria`, `questions_to_answer`, `development_guidance`, …) conforme schema GET-PACKAGE.

- `core_idea`: afirmação técnica verificável (não “escrever sobre X”).
- `must_include`: obrigações concretas, não slogans.
- `open_questions`: lacunas honestas; se dependem de norma/PDF → sinalizar **get-research**.

Candidatos paralelos (no chat ou secção do pacote): novos `TerminologyConcept`, `Reference` — commit via app/get-lexicon, não inventar UUIDs protegidos.

## PROPOSE — saída

1. Pacote GET-PACKAGE completo ou diff claro por `point_id`.
2. Lista **«Alterações por ponto»** em prosa (o que mudou e porquê).
3. Secção **«Para get-research»** se houver lacunas documentais.
4. **Não** incluir `status: ready` / `approved` nos pontos — marcação é humana na UI após import.

Validar mentalmente contra regras da app (`validate_point`): título, ideia central, listas mínimas antes de sugerir ao engenheiro marcar ready.

## Proibido

- Marcar `ready`, `approved` ou campos protegidos no JSON devolvido.
- Inventar requisitos sem suporte no export ou corpus citado.
- Reorganizar fascículo inteiro ou misturar knowledge/pontos/estrutura no mesmo ficheiro (ritual F0).
- Consolidar import ou assumir staging aceite.
- Substituir decisão humana sobre o que entra no SQLite.

Ver `reference.md` e `examples.md`.