# F0 Phase A — Inventário do incidente (canal de import)

Usar quando o canal não é conhecido (ex.: reestruturação na LLM + import com estrutura baralhada).

## Onde procurar no workspace

Raiz: `GET_WORKSPACE_ROOT` ou `~/.get` / configurado na app.

| Local | Indício |
|-------|---------|
| `{workspace}/imports/` | Ficheiros JSON carregados; subpastas por run |
| `{workspace}/exports/` | Export original (`EXP-…`) para three-way |
| UI → Reimportar → lista de importações | `package_type`, `schema_name`, data |
| `migration_reports/` | Se foi **workbook** (`migrate`) |
| Block editor → «Exportar pacote» / «Importar» | GET-PACKAGE bloco recente |

## Identificar canal

| Canal | Sinais |
|-------|--------|
| **GET-PACKAGE block** | `schema: GET-PACKAGE`, `scope.kind: block`, import via bloco ou `/packages/import` |
| **GET-PACKAGE fascicle** | `scope.kind: fascicle`, payload com `fascicle`, `editable_knowledge` |
| **Workbook** | `.xlsx` em imports, relatório `workbook-import-v1`, folhas 01_Fasciculos, 02_Blocos, … |
| **Fascicle roundtrip legado** | `schema_name` fascicle-roundtrip na lista de imports |

Abrir o ficheiro devolvido pela LLM:

- Topo com `"schema": "GET-PACKAGE"` → pacote unificado.
- Excel com múltiplas folhas misturadas pela LLM → risco alto de confusão conceptual ([WORKBOOK_GET_MAP.md](../WORKBOOK_GET_MAP.md)).

## Perguntas para o retro

1. Pediste à LLM «reorganizar lista/estrutura» num único passo?
2. Alterou pontos + knowledge + estrutura no mesmo JSON?
3. Consolidaste tudo de uma vez (batch)?
4. Havia backup imediatamente antes?

## Acções imediatas

1. `GET /api/backups` — listar; criar backup crítico do estado **actual** (documentar).
2. Se existir backup **anterior** ao import: planear restauro ([WORKSPACE_OPERATIONS.md](../WORKSPACE_OPERATIONS.md)).
3. Se não: escolher fascículo **piloto** separado (ou corrigir manualmente árvore) antes de novo roundtrip.
4. Preencher [micro-F0-retro-TEMPLATE.md](micro-F0-retro-TEMPLATE.md) secção «Estado inicial».

## Estado Phase A

| Campo | Valor |
|-------|--------|
| Canal confirmado | _preencher_ |
| Data incidente | _preencher_ |
| Fascículo/bloco afectado | _preencher_ |
| Backup de recuperação disponível | sim / não |
| Decisão | restaurar / corrigir manual / piloto noutro fascículo |

Quando esta tabela estiver completa, avançar para o [ritual](micro-F0-import-ritual.md) Phase C.