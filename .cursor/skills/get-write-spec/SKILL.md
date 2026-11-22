---
name: get-write-spec
description: Redige texto do caderno a partir do ZIP GET-LLM; artefacto MD fora do GET, sem reimportar como verdade.
disable-model-invocation: true
---

# get-write-spec — redação externa (READ → AUTHOR)

Comportamento canónico: `docs/GET_SKILLS_PLAN.md` (get-write-spec). Macro F2 / entrega **M2**.

## Pré-requisitos

- Pontos alvo em **`ready`** ou **`approved`** (ou rascunhos só se export pediu `include_draft`).
- Export **GET-LLM** recente (`llm_generation_{profile}.zip`) do projecto ou fascículo. Pré-voo: `backend/scripts/f2_m2_preflight.py --export`.

## Modo

- Ciclo: **READ → AUTHOR** (Markdown ou texto para Word noutra ferramenta).
- **Não** é ciclo PROPOSE para SQLite: o GET não recebe o `.md` como autoridade.

## Contexto mínimo

1. ZIP GET-LLM descompactado ou anexo: `master_*_llm.json`, `manifest.json`, blocos/fascículos necessários.
2. **`terminology_{profile}_llm.md`** e/ou `.json` — vocabulário vinculativo (E05).
3. `generation_rules`, `llm_freedom` por ponto (`strict` vs `exploratory`).
4. Âmbito explícito: bloco (`display_code`) ou fascículo — **não** projecto inteiro de uma vez salvo pedido.

## Regras de redação

- Respeitar `must_include`, `limits_and_exclusions`, premissas e `avoid_terms` / overrides do glossário.
- Léxico estrutural (capítulo/ponto) nos MD derivados do export — não renomear nós técnicos por capricho.
- Conteúdo **exploratory** ou não aprovado: marcar claramente (secção «Sugestões não aprovadas» ou nota marginal).
- Não inventar requisitos além do registado nos pontos; lacunas → nota para **get-review**, não preencher como facto.

## Saída

- Ficheiro `.md` (secções alinhadas ao bloco/fascículo exportado) ou indicação de destino Word.
- Opcional: índice de pontos cobertos ↔ secções do texto.

## Proibido

- Alterar SQLite, usar GET-PACKAGE como saída de redação em vez de MD, ou reimportar MD na app.
- Aprovar conteúdo ou marcar pontos `ready`/`approved`.
- Ignorar glossário técnico do ZIP.
- Misturar redação de vários fascículos num único ficheiro sem pedido explícito.

## Handoff

Texto → **get-review** → correcções via GET-PACKAGE aceites pelo engenheiro.

Ver `reference.md` e `examples.md`.