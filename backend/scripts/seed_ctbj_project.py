"""Cria o projeto CTBJ a partir da estrutura Markdown GET."""

from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.deps import get_settings
from app.domain.block.schemas import (
    BlockHeaderPatch,
    DevelopmentPointCreate,
    DevelopmentPointPatch,
    PointLists,
    PremiseCreate,
)
from app.domain.block.service import create_point, create_premise, get_point, patch_block, patch_point
from app.schemas.document import DocumentNodeCreateRequest
from app.schemas.knowledge import KnowledgeCreateRequest
from app.schemas.project import ProjectCreateRequest
from app.schemas.reference import ReferenceCreateRequest
from app.schemas.terminology import TerminologyCreateRequest
from app.services.document_service import create_document_node, list_document_nodes
from app.services.knowledge_service import create_item
from app.services.project_service import create_project, list_projects, list_templates
from app.services.reference_service import create_reference
from app.services.terminology_service import create_terminology

DEFAULT_MD = Path(r"F:\MyFiles\Downloads\Estrutura_GET_CTBJ_Belo_Jardim.md")
PROJECT_NAME = (
    "Remodelação do sistema de comando e controlo da Central Termoelétrica de Belo Jardim"
)
ORIGIN = "Estrutura_GET_CTBJ_Belo_Jardim.md"
DEFAULT_GUIDANCE = (
    "Desenvolver apenas com factos e decisões já aprovados; distinguir o que está em aberto; "
    "não inventar requisitos quantitativos, marcas ou arquitecturas não decididas."
)
INTENDED_OUTCOME = (
    "O tópico fica descrito no caderno de encargos com fronteiras claras, "
    "sem inventar requisitos não fornecidos."
)
TARGET_OUTPUT = {
    "format": "spec_section",
    "language": "pt-PT",
    "tone": "formal_technical",
}

FASCICLE_RE = re.compile(r"^# (F\d{2}) — (.+)$")
BLOCK_RE = re.compile(r"^## ((F\d{2})_B\d{2}) — (.+)$")
BULLET_RE = re.compile(r"^(\s*)- (.+)$")
NUMBERED_RE = re.compile(r"^\d+\.\s+\*\*(.+?)\*\*\.?\s*$")

STANDARDS = [
    ("IEC 81346", "Referenciação e identificação de objetos da instalação."),
    ("IEC 61175-1", "Designação semântica de sinais."),
    ("ISA-5.1", "Instrumentação e P&ID, quando aplicável."),
    ("IEC 63303 / ISA-101", "Princípios de HMI."),
    ("ISO 11064", "Ergonomia de salas e postos de comando, quando aplicável."),
    ("IEC 62443", "Cibersegurança de IACS."),
    ("ISA-18.2 / IEC 62682", "Gestão de alarmes, quando adotadas como referências do projeto."),
]

TERMS = [
    {
        "preferred_term": "Sistema de controlo distribuído",
        "acronym": "DCS",
        "definition": "Arquitetura de automação em que controlo, I/O e supervisão estão integrados numa plataforma distribuída.",
        "domain": "automação",
    },
    {
        "preferred_term": "Supervisory Control and Data Acquisition",
        "acronym": "SCADA",
        "definition": "Camada de supervisão e aquisição de dados, tipicamente sobre controladores de processo.",
        "domain": "automação",
    },
    {
        "preferred_term": "Controlador lógico programável",
        "acronym": "PLC",
        "definition": "Controlador industrial para lógica, sequências e regulação local de processo.",
        "domain": "automação",
    },
    {
        "preferred_term": "Interface homem-máquina",
        "acronym": "HMI",
        "definition": "Camada de operação humana: mímicos, faceplates, alarmes e comandos.",
        "domain": "operação",
    },
    {
        "preferred_term": "Historian",
        "acronym": None,
        "definition": "Sistema de arquivo histórico de medidas, estados e eventos operacionais.",
        "domain": "dados",
    },
    {
        "preferred_term": "Zona desmilitarizada industrial",
        "acronym": "iDMZ",
        "definition": "Fronteira OT/IT para publicação de dados, sem autoridade de comando sobre o processo.",
        "domain": "cibersegurança",
    },
    {
        "preferred_term": "Datalist mestre",
        "acronym": None,
        "definition": "Artefacto estruturante da migração e rastreabilidade entre as-is, to-be, software, HMI, alarmes, I/O, testes e as-built.",
        "domain": "dados",
    },
    {
        "preferred_term": "Matriz de Alocação Funcional",
        "acronym": None,
        "definition": "Matriz que define onde reside cada função, autoridade de comando, dependências, fallback, alarmes, estados e critérios de aceitação.",
        "domain": "controlo",
    },
]


def parse_structure(text: str) -> dict:
    principles: list[str] = []
    artefacts: list[str] = []
    fascicles: list[dict] = []
    current_fascicle: dict | None = None
    current_block: dict | None = None
    current_point: dict | None = None
    section = "head"

    for raw in text.splitlines():
        line = raw.rstrip()
        if FASCICLE_RE.match(line):
            section = "structure"
            m = FASCICLE_RE.match(line)
            current_fascicle = {"code": m.group(1), "title": m.group(2).strip(), "blocks": []}
            fascicles.append(current_fascicle)
            current_block = None
            current_point = None
            continue
        if line.startswith("# Artefactos"):
            section = "artefacts"
            current_fascicle = None
            current_block = None
            current_point = None
            continue
        if line.startswith("# Nota de utilização"):
            section = "note"
            continue
        if line.startswith("## Princípios transversais"):
            section = "principles"
            continue
        if BLOCK_RE.match(line) and current_fascicle is not None:
            m = BLOCK_RE.match(line)
            current_block = {"code": m.group(1), "title": m.group(3).strip(), "points": []}
            current_fascicle["blocks"].append(current_block)
            current_point = None
            continue
        if section == "principles":
            m = BULLET_RE.match(line)
            if m and not m.group(1):
                principles.append(m.group(2).strip())
            continue
        if section == "artefacts":
            m = NUMBERED_RE.match(line)
            if m:
                artefacts.append(m.group(1).strip())
            continue
        if current_block is None:
            continue
        m = BULLET_RE.match(line)
        if not m:
            continue
        indent, body = m.group(1), m.group(2).strip()
        if indent == "":
            current_point = {"title": _strip_period(body), "guidance": []}
            current_block["points"].append(current_point)
        elif current_point is not None:
            current_point["guidance"].append(_strip_period(body))

    return {
        "principles": principles,
        "artefacts": artefacts,
        "fascicles": fascicles,
    }


def _strip_period(text: str) -> str:
    return text[:-1] if text.endswith(".") else text


def pick_template(fascicle_code: str, block_title: str) -> str | None:
    t = block_title.lower()
    if fascicle_code == "F12" or "ciber" in t:
        return "cybersecurity_requirement"
    if fascicle_code == "F14" or any(k in t for k in ("ensaio", "fat", "sat", "teste", "validação", "comissionamento")):
        return "test_requirement"
    if any(k in t for k in ("falha", "perda de refer", "degradad", "rollback", "contingência")):
        return "failure_behavior"
    if "interface" in t:
        return "interface_requirement"
    if "manuten" in t or "sobressalent" in t:
        return "maintenance_requirement"
    if "decisão" in t or "seleção da solução" in t:
        return "pending_decision"
    if any(k in t for k in ("filosofia", "princípio", "neutralidade", "visão corporativa")):
        return "architecture_principle"
    if any(k in t for k in ("comando", "operação", "modos", "alarme", "hmi", "migração")):
        return "operational_requirement"
    return None


def premise_meta(statement: str) -> tuple[str, str]:
    lower = statement.lower()
    if lower.startswith("possibilidade"):
        return "recommended", "project_decision"
    if "neutralidade" in lower or "falha de comunicações" in lower or "perda de referência" in lower:
        return "mandatory", "eda_philosophy"
    if "matriz de alocação" in lower or "datalist" in lower:
        return "mandatory", "functional_requirement"
    return "mandatory", "eda_philosophy"


def main() -> None:
    md_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MD
    text = md_path.read_text(encoding="utf-8")
    parsed = parse_structure(text)
    if not parsed["fascicles"]:
        raise SystemExit("Nenhum fascículo encontrado no Markdown.")

    get_settings.cache_clear()
    settings = get_settings()

    existing = [p for p in list_projects(settings) if p.name == PROJECT_NAME]
    if existing:
        raise SystemExit(f"O projeto já existe: {existing[0].id}")

    templates = list_templates(settings)
    if not templates or not templates[0].versions:
        raise SystemExit("Modelo de projeto em falta.")
    template_version_id = templates[0].versions[0].id

    project = create_project(
        settings,
        ProjectCreateRequest(
            template_version_id=template_version_id,
            name=PROJECT_NAME,
            intervention_type="brownfield",
        ),
    )
    project_id = project.id
    print(f"Projeto criado: {project_id}")

    create_item(
        settings,
        KnowledgeCreateRequest(
            title="Enquadramento CTBJ — remodelação DCS/SCADA",
            content=(
                "Instalação: Central Termoelétrica de Belo Jardim (CTBJ), Canada dos Pastos, Praia da Vitória. "
                "Objetivo: índice modular para desenvolvimento futuro do Caderno de Encargos segundo o método GET. "
                "Regra: cada bloco contém pontos controlados pelo utilizador, posteriormente desenvolvidos de forma autónoma. "
                "Estado de origem: estrutura de trabalho consolidada no ficheiro "
                f"{md_path.name}."
            ),
            origin_context=ORIGIN,
            scope_type="project",
            scope_id=project_id,
            knowledge_type="fact",
        ),
    )

    for statement in parsed["principles"]:
        importance, source = premise_meta(statement)
        create_premise(
            settings,
            PremiseCreate(
                owner_kind="project",
                owner_id=project_id,
                statement=_strip_period(statement),
                importance=importance,  # type: ignore[arg-type]
                source_type=source,  # type: ignore[arg-type]
                confidence="confirmed",
                notes="Princípio transversal da estrutura GET CTBJ.",
            ),
        )
        create_item(
            settings,
            KnowledgeCreateRequest(
                title=statement[:120],
                content=statement,
                origin_context=ORIGIN,
                scope_type="project",
                scope_id=project_id,
                knowledge_type="principle",
            ),
        )

    for artefact in parsed["artefacts"]:
        create_item(
            settings,
            KnowledgeCreateRequest(
                title=f"Artefacto transversal: {artefact}",
                content=(
                    f"Artefacto recomendado para a remodelação CTBJ: {artefact}. "
                    "Tratar como plano de conhecimento, não como texto contratual já aprovado."
                ),
                origin_context=ORIGIN,
                scope_type="project",
                scope_id=project_id,
                knowledge_type="authoring_instruction",
            ),
        )

    for title, notes in STANDARDS:
        create_reference(
            settings,
            ReferenceCreateRequest(
                scope_type="project",
                scope_id=project_id,
                title=title,
                citation=title,
                notes=notes,
            ),
        )

    for term in TERMS:
        create_terminology(
            settings,
            TerminologyCreateRequest(
                scope_type="project",
                scope_id=project_id,
                preferred_term=term["preferred_term"],
                definition=term["definition"],
                acronym=term["acronym"],
                domain=term["domain"],
                language="pt",
                notes="Vocabulário inicial do projeto CTBJ.",
            ),
        )

    fascicle_ids: dict[str, str] = {}
    for fascicle in parsed["fascicles"]:
        created = create_document_node(
            settings,
            project_id,
            DocumentNodeCreateRequest(node_type="fascicle", title=fascicle["title"], parent_id=None),
        )
        fascicle_ids[fascicle["code"]] = created.node.id
        print(f"  {created.node.display_code} {fascicle['title']}")

    point_count = 0
    block_count = 0
    for fascicle in parsed["fascicles"]:
        parent_id = fascicle_ids[fascicle["code"]]
        for block in fascicle["blocks"]:
            created = create_document_node(
                settings,
                project_id,
                DocumentNodeCreateRequest(
                    node_type="block",
                    title=block["title"],
                    parent_id=parent_id,
                ),
            )
            block_id = created.node.id
            block_count += 1
            point_titles = [p["title"] for p in block["points"]]
            scope = (
                "Pontos previstos neste bloco: " + "; ".join(point_titles) + "."
                if point_titles
                else "Âmbito a detalhar a partir da estrutura GET CTBJ."
            )
            patch_block(
                settings,
                block_id,
                BlockHeaderPatch(
                    objective=(
                        f"Preparar «{block['title']}» para o caderno de encargos da "
                        "remodelação do sistema de comando e controlo da CTBJ."
                    ),
                    scope=scope,
                    target_output=TARGET_OUTPUT,
                ),
            )
            template_id = pick_template(fascicle["code"], block["title"])
            for point in block["points"]:
                created_point = create_point(
                    settings,
                    block_id,
                    DevelopmentPointCreate(title=point["title"], template_id=template_id),
                )
                current = get_point(settings, created_point.id)
                lists = current.lists or PointLists()
                guidance = list(point["guidance"]) if point["guidance"] else [DEFAULT_GUIDANCE]
                lists.development_guidance = guidance
                patch_point(
                    settings,
                    created_point.id,
                    DevelopmentPointPatch(
                        core_idea=point["title"],
                        intended_outcome=INTENDED_OUTCOME,
                        llm_freedom="bounded",
                        lists=lists,
                    ),
                )
                point_count += 1

    nodes = list_document_nodes(settings, project_id).nodes
    print(
        f"Concluído: {len(fascicle_ids)} fascículos, {block_count} blocos, "
        f"{point_count} pontos, {len(nodes)} nós documentais. id={project_id}"
    )


if __name__ == "__main__":
    main()
