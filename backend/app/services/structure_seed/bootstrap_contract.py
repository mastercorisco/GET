"""Gerar GET-STRUCTURE-CONTRACT a partir de catálogos registados."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.structure_seed.registry import get_registry_entry, load_catalog

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_VERSION = "1.0.0"


def build_bootstrap_contract(catalog_id: str) -> dict:
    entry = get_registry_entry(catalog_id)
    catalog = load_catalog(catalog_id)
    fascicles = []
    for f in catalog.fascicles:
        blocks = [
            {
                "display_code": b.code,
                "title": b.title,
                "development_point_hints": list(b.development_points),
            }
            for b in f.blocks
        ]
        row = {"display_code": f.code, "title": f.title, "blocks": blocks}
        if f.purpose:
            row["purpose"] = f.purpose
        fascicles.append(row)

    return {
        "schema": "GET-STRUCTURE-CONTRACT",
        "schema_version": SCHEMA_VERSION,
        "catalog": {
            "id": catalog.id,
            "version": catalog.version,
            "checksum": catalog.checksum,
            "display_name": catalog.display_name or entry.display_name,
        },
        "project_template_code": entry.project_template_code,
        "fascicles": fascicles,
        "editorial_rules": [
            "A árvore fascículo/bloco entra pela criação do projecto (seed) ou pelo workbook 01/02.",
            "GET-PACKAGE não cria nós novos; serve para conteúdo após baseline.",
            "Não inferir eliminações por omissão no JSON devolvido.",
        ],
        "llm_instructions": [
            "Use os códigos display_code como referência estável; não renumerar fascículos.",
            "Produza conteúdo editorial (objectivos, pontos, conhecimento) alinhado com cada bloco.",
            "Devolver alterações em GET-PACKAGE (fascicle/block) após o utilizador criar o projecto e publicar baseline.",
            "Distinção entre regra normativa, convenção corporativa e instância de projecto quando aplicável.",
        ],
        "anti_patterns": [
            "Inventar códigos de bloco fora do catálogo sem processo de extensão.",
            "Substituir o contrato bootstrap por um GET-PACKAGE e esperar reimportação da árvore inteira.",
            "Comprimir ou renumerar lacunas de numeração documental deliberadas.",
        ],
        "workbook_mapping": {
            "fascicles_sheet": "01_Fasciculos",
            "blocks_sheet": "02_Blocos",
            "notes": "Coluna de código na linha 4+; reimportação via ecrã Importação Excel (workbook-import-v1).",
        },
        "next_steps": [
            "Abrir workspace GET e criar projecto com o modelo indicado em project_template_code.",
            "Opcional: transferir workbook-structure.xlsx e ajustar folhas 01/02 antes de consolidar.",
            "Publicar baseline no projecto.",
            "Exportar GET-PACKAGE por fascículo na Preparação do bloco ou ecrã Exportar.",
        ],
    }


def bootstrap_contract_json(catalog_id: str) -> str:
    return json.dumps(build_bootstrap_contract(catalog_id), ensure_ascii=False, indent=2) + "\n"