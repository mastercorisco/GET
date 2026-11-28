# Fase 2 — Registar RDS pedagógico v4 como catálogo (dados)

Este documento descreve passos **sem implementação automática** no repositório até existir inventário aprovado.

## Pré-requisitos

- Markdown fonte (ex. `Estrutura_Nova_RDS_EDA_Pedagogica_v4_com_Anexo_Regras.md`).
- Acordo sobre códigos estáveis (`F00`…`F18`, blocos `Fnn_Bmm`).

## Passos

1. Copiar/curar inventário para `docs/inventory/rds_pedagogic_v4.inventory.md` (formato `# Fascículo` / `## Bloco`).
2. Compilar:  
   `python scripts/compile_structure_catalog.py --input docs/inventory/rds_pedagogic_v4.inventory.md --output catalogs/rds_pedagogic_v4.pt-PT.json --id rds_pedagogic_v4 --version 1 --display-name "RDS EDA pedagógico v4"`.
3. Validar contra `schemas/structure_catalog.schema.json`.
4. Registar em `backend/app/services/structure_seed/registry.py` (`CatalogRegistryEntry` + path).
5. Adicionar `ProjectTemplate` `rds-pedagogic-v4` v1 em `_ensure_templates` com metadata `structure_catalog.id = rds_pedagogic_v4`.
6. Opcional: `catalogs/rds_pedagogic_v4_rules.pt-PT.json` para regras K.28 referenciadas no contrato bootstrap (campo `editorial_rules` enriquecido em `bootstrap_contract.py` por catálogo).
7. Testes de integração: contagens esperadas (19 fascículos, ~110 blocos) + amostra de seed.

## Não fazer na fase 2

- Alterar `get_package.schema.json` para criar nós novos via import.
- Embutir texto integral do Anexo K no SQLite (usar referência ou biblioteca).