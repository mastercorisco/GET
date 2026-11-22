# Micro-plano — glossário técnico no pacote GET-LLM (F2 / T0)

**Macro:** [GET_MACRO_PLAN.md](../GET_MACRO_PLAN.md) §2.1, F2, T0.  
**ADR:** ADR-061.

## Objectivo

Incluir vocabulário controlado (`TerminologyConcept` + overrides) como Markdown no ZIP `llm_generation_{profile}.zip`, para sessões de redação externa (ex. Claude) alinhadas com o caderno de encargos.

## Fora de âmbito

- Servidor MCP; `GET /api/terminology/search`; staging de propostas.
- Reimportação do glossário MD.
- JSON canónico de terminologia no pacote (fase futura opcional).
- Preencher `protected_context.terminology` no roundtrip fascículo.

## Implementação

| Componente | Ficheiro |
|------------|----------|
| Snapshot SQLite | `backend/app/services/llm_export/terminology_snapshot.py` |
| Render MD | `backend/app/services/llm_export/render_terminology_md.py` |
| Orquestração ZIP/manifest | `backend/app/services/llm_export/orchestrate.py` |
| Ponteiro no master MD | `backend/app/services/llm_export/render_md.py` (`package_terminology_markdown`) |

### Conteúdo do MD

- Cabeçalho: aviso não reimportável, `export_id`, perfil, data.
- Secções: biblioteca; termos de projecto; overrides (legado, evitar, nota).
- Ordenação por `preferred_term`.

### Manifest

- Ficheiro: `terminology_{profile}_llm.md`
- `kind`: `terminology_glossary`
- `sha256` do conteúdo UTF-8.

### Master

- Campo opcional `package_terminology_markdown` no JSON mestre.
- Secção «Glossário técnico (vocabulário)» no `master_{profile}_llm.md`.

## Critérios de aceitação

- [x] ZIP contém `terminology_{profile}_llm.md` para o perfil do pedido.
- [x] `manifest.files` inclui entrada `terminology_glossary` com `sha256` correcto.
- [x] Termos da biblioteca e do projecto aparecem quando existem na BD.
- [x] Overrides listados com `legacy_term` / `avoid_in_project` quando aplicável.
- [x] `master_*_llm.md` referencia o ficheiro de glossário (distinto de «Glossário (produção de texto)»).
- [x] Teste de integração `test_llm_generation_export` cobre presença no ZIP e manifest.
- [x] `GET_APP_SPECIFICATION.md` e `ARCHITECTURE_DECISIONS.json` (ADR-061) actualizados.

## Verificação manual

1. Registar ≥1 termo na biblioteca e (opcional) override no projecto.
2. Export `POST /api/projects/{id}/exports/llm-generation`.
3. Abrir ZIP: ler `terminology_*_llm.md` e `master_*_llm.md`.
4. Colocar pasta do export num projecto Claude; confirmar que o glossário orienta redação.