# Mapa de importação — workbook GET v1

Convenção comum a todas as folhas de dados:

- Linhas 1–3: título e notas (não importadas como entidades).
- **Linha 4:** cabeçalhos canónicos (não alterar nos modelos controlados).
- **Linha 5+:** dados.

Versão do mapeamento: `workbook-import-v1` (ver `schemas/workbook-import-v1.schema.json`).

## Folhas

| Folha | Destino MVP |
|-------|-------------|
| `00_Leitura` | `migration_report.project_context` (metadados narrativos) |
| `01_Fasciculos` | `document_node` (`fascicle`) |
| `02_Blocos` | `document_node` (`block`), pai pelo código de fascículo (coluna Fascículo) |
| `03_Filosofia_Controlo` | `knowledge_item` (`principle`), âmbito `project` |
| `04_Artefactos_GET` | `knowledge_item` (`decision`); `library` se texto indicar reutilização |
| `05_A01_Alocacao` | `technical_instance` (`kind=function`, `export_code=function_id`) |
| `06_Mapa_Normativo` | `reference` (`library`) |

## Fluxo operacional

Pela **UI** (ecrã «Importação Excel») ou **API**:

| Passo | UI / API | Efeito |
|-------|----------|--------|
| 1 | Transferir modelo | Download `GET /api/workbook/templates/{id}` |
| 2 | `POST /api/workbook/validate` | Validação estrutural (sem BD) |
| 3 | `POST /api/workbook/migrate` (multipart, `dry_run=true`) | Upload para `{workspace}/imports/workbook/{run_id}/source.xlsx` + relatório |
| 4 | `POST /api/workbook/migrate/apply` | Backup crítico; `new_project` ou `existing_project` |

Relatório: `{workspace}/migration_reports/{run_id}/report.json`. Consulta: `GET /api/workbook/migration-reports/{run_id}`.

Equivalente **CLI**:

1. `python scripts/workbook_inspect.py` — inventário e contagens.
2. `python scripts/migrate_workbook_get.py --workspace-root PATH` — **dry-run**.
3. Revisão humana do relatório.
4. `... --apply --confirm I_UNDERSTAND` — backup crítico + consolidação (novo projecto).

## Workbook de referência

`C:\PROGRAMACAO\GET_aux\GET_Estrutura_CE_Belo_Jardim_v1.xlsx` (Remodelação CE Belo Jardim).

Inventário gerado: `examples/legacy/workbook-inventory.json` (opcional, via `workbook_inspect --json-out`).