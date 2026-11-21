# F0 Phase A — Inventário (workspace testes)

**Workspace:** `C:\PROGRAMACAO\GET_aux\testes` (via `~/.get/app-config.json`)  
**Projecto (CTBJ):** `976e3991-e64e-4306-99fe-4ac1e2230b52`  
**Data inventário:** 2026-11-21  
**Estado reportado pelo utilizador:** parcialmente corrigido manualmente; avançar com piloto após Phase A.

## Canal do incidente (conclusão)

| Canal | Evidência | Probabilidade |
|--------|-----------|---------------|
| **GET-PACKAGE `scope.kind=block`** | Múltiplos imports `F01_B02_package_completo.json`, `F04_B07_package_atualizado.json`; exports `PKG-BLK-F01_B02`, `PKG-BLK-F04_B07` | **Alta** |
| GET-PACKAGE fascículo | Export `PKG-FASC-F01/F01_package.json` existe; menos pastas `imports` fascículo | Média (uso futuro piloto estrutura) |
| Workbook Excel | `exports/workbook/*.xlsx` (2026-11-16); sem import workbook recente na pasta | Baixa para o incidente da “lista” |
| Estrutura MD/PDF/XMind | Muitos `exports/document-structure/*` (2026-11-18) | Possível confusão **visual** de estrutura (artefacto derivado, não reimportável) |

**Contrato listas (Onda 1):** `development_guidance`, `perspectives` e `acceptance_criteria` são **strings**; `must_include` / `open_questions` são **objectos**. O brief exportado antigo podia induzir o oposto — corrigido na app.

**Exports obsoletos:** re-export obrigatório antes de qualquer sessão LLM. Em `testes`, F01 tem apenas `F01_B01`…`F01_B06`; pacotes com `F01_B07` ou UUID CTBJ v3 antigos falham na validação de identidade (`block_id` / `display_code`). Confirmar `export_record` na UI e hash do ficheiro em disco; não confiar em `PKG-FASC-F01` ou `PKG-BLK-*` copiados sem registo actual.

**Hipótese de causa:** sessões LLM com pacotes **bloco “completo”** (conteúdo + muitos pontos) e/ou reorganização conceptual fora do modo F0-*; imports repetidos sobre **F01_B02** (≥6 tentativas). Validação estrita pode passar com **avisos** (strings em `development_guidance`).

## Backups disponíveis

Pasta: `{workspace}/backups/critical/`

- `get_critical_20261121T191345Z.db` — mais recente
- Vários de 2026-11-18 e 2026-11-17 (anteriores a exportações estruturais)

**Decisão Phase A:** não restaurar (utilizador corrigiu manualmente). Usar backup **antes** do próximo consolidate.

## Ficheiros-chave

| Papel | Caminho |
|--------|---------|
| Export base F04_B07 | `exports/PKG-BLK-F04_B07/F04_B07_package.json` |
| Import recente F04_B07 | `imports/c433797e-.../F04_B07_package_atualizado.json` |
| Export fascículo F01 (piloto estrutura) | `exports/PKG-FASC-F01/F01_package.json` |
| Série F01_B02 | `exports/PKG-BLK-F01_B02/`, `imports/* /F01_B02_package_*.json` |

## Validação offline (exemplo)

```powershell
cd C:\PROGRAMACAO\GET\backend
python scripts/validate_get_package_file.py "C:\PROGRAMACAO\GET_aux\testes\imports\c433797e-7f68-4d1b-a255-8c6a19b90544\F04_B07_package_atualizado.json" --project-id 976e3991-e64e-4306-99fe-4ac1e2230b52
```

Resultado 2026-11-21: OK estrito; avisos anteriores em `development_guidance` eram falso positivo do script F0 (strings são correctas).

## Próximo passo F0 (Phase C)

1. **Backup crítico** na app.
2. Piloto **F0-structure** no fascículo **F01** usando export `PKG-FASC-F01` (não bloco “completo”).
3. Instrução LLM: modo `F0-structure` em [micro-F0-import-ritual.md](micro-F0-import-ritual.md).
4. Validar JSON → import → aceitar **só** propostas estruturais → consolidate → re-export.

Blocos **F01_B02** / **F04_B07**: usar depois modo **F0-content-block**, um bloco de cada vez, após fascículo estável.

## Estado Phase A

| Campo | Valor |
|-------|--------|
| Canal confirmado | GET-PACKAGE **block** (incidente); piloto estrutura via **fascicle** |
| Backup de recuperação | Disponível; não usado |
| Decisão | Correcção manual feita; piloto F01-structure a seguir |