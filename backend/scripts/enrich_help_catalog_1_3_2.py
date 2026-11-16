"""Atualiza get_help_catalog.pt-PT.json v1.3.2 — GET-PACKAGE vs GET-LLM vs estrutura."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalogs" / "get_help_catalog.pt-PT.json"


def field(
    label: str,
    short_help: str,
    definition: str,
    guiding_question: str,
    *,
    purpose: str,
    workflow: str,
    when: str,
    next_step: str,
    concepts: list[str],
    screen: str,
    confusions: list[str],
    tips: list[str] | None = None,
    instructions: str = "",
) -> dict:
    return {
        "label": label,
        "short_help": short_help,
        "definition": definition,
        "guiding_question": guiding_question,
        "instructions": instructions or (tips[0] if tips else ""),
        "good_examples": [],
        "bad_examples": [],
        "tips": tips or [],
        "allow_use_example": False,
        "purpose_in_app": purpose,
        "workflow_context": workflow,
        "when_to_use": when,
        "what_happens_next": next_step,
        "related_concepts": concepts,
        "related_screen": screen,
        "common_confusions": confusions,
    }


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    data["catalog_version"] = "1.3.2"
    fields = data.setdefault("fields", {})
    concepts = data.setdefault("concepts", {})
    screens = data.setdefault("screens", {})
    workflows = data.setdefault("workflows", {})
    method = data.setdefault("method", {})

    concepts["get_package"] = {
        "label": "GET-PACKAGE",
        "summary": "Um JSON ida e volta para discutir na LLM e reimportar alterações.",
        "role_in_get": (
            "Contrato get_package.schema.json: um ficheiro por bloco ou fascículo, com rules_hash. "
            "Exporta preparação e/ou conhecimento; a devolução entra em Reimportar para merge e aprovação."
        ),
        "not_this": (
            "Não é GET-LLM (só leitura), exportação estrutural MD/PDF/XMind, nem fascicle_roundtrip legado."
        ),
    }

    fields["block.export_panel"] = field(
        "Pacote e LLM (bloco)",
        "Dois fluxos no mesmo painel: GET-PACKAGE (reimportável) e GET-LLM (só leitura).",
        "A Preparação do bloco separa discussão com retorno à app da geração de texto sem reimportação.",
        "Quer devolver alterações à app ou só gerar texto na LLM?",
        purpose="Evitar trocar contratos na mesma sessão de trabalho.",
        workflow="Preparação do bloco — painel «Pacote e LLM».",
        when="Sempre que exportar a partir de um bloco.",
        next_step="Escolha «Exportar pacote» para ida/volta; GET-LLM apenas para redação offline.",
        concepts=["get_package", "exchange_package", "block"],
        screen="block-editor",
        confusions=[
            "Prima «Exportar pacote» para GET-PACKAGE; «Exportar GET-LLM» não reimporta.",
        ],
        tips=[
            "Ordem sugerida: pontos ready → baseline (fascículo/projecto) → Exportar pacote.",
            "Importar pacote no bloco abre Reimportar e inicia a análise das alterações.",
        ],
        instructions="Leia os cartões por ordem: primeiro GET-PACKAGE, depois GET-LLM.",
    )

    fields["block.get_package"] = field(
        "GET-PACKAGE (bloco)",
        "Um JSON por bloco para discutir na LLM e reimportar.",
        "scope_kind block em get_package.schema.json; merge de objectivo, pontos e premissas do bloco.",
        "Vai discutir este bloco na LLM e trazer propostas de volta?",
        purpose="Ciclo curto bloco-a-bloco sem exportar o fascículo inteiro.",
        workflow="Preparação do bloco — cartão «Pacote para discussão (ida e volta)».",
        when="Revisão técnica de um bloco com retorno estruturado.",
        next_step="Após importar, rever propostas em Reimportar e consolidar.",
        concepts=["get_package", "baseline", "development_point"],
        screen="block-editor",
        confusions=["Não usar «Exportar GET-LLM» para este fluxo."],
        tips=[
            "Requer baseline publicada no projecto.",
            "Omissão de campos no JSON devolvido não apaga conteúdo aprovado.",
        ],
    )

    fields["export.get_package"] = field(
        "GET-PACKAGE (fascículo)",
        "Um JSON por fascículo (raiz) para discussão e reimportação.",
        "scope_kind fascicle; reutiliza merge de conhecimento do fascículo no mesmo ficheiro.",
        "Vai discutir um domínio inteiro (ex. F04) com retorno à app?",
        purpose="Pacote único preferível ao fascicle_roundtrip legado para a maioria dos casos.",
        workflow="Ecrã Exportar — cartão «Pacote para discussão (fascículo)».",
        when="Após baseline, para trabalho por fascículo com LLM externa.",
        next_step="Reimportar o mesmo ficheiro em Incorporar pacote.",
        concepts=["get_package", "baseline", "fascicle"],
        screen="export",
        confusions=[
            "Não confundir com «Geração LLM (GET-LLM)» no cartão abaixo.",
            "Não confundir com «Exportar fascículo roundtrip» (formato legado).",
        ],
        tips=[
            "Seleccione o fascículo raiz no selector deste cartão, não no roundtrip legado.",
        ],
    )

    fields["import.get_package"] = field(
        "Incorporar GET-PACKAGE",
        "Carregue o JSON devolvido pela LLM (schema GET-PACKAGE).",
        "Validação estrita: falha de schema, rules_hash ou âmbito rejeita o ficheiro inteiro.",
        "O ficheiro tem schema GET-PACKAGE e o mesmo export_id?",
        purpose="Entrada controlada das alterações propostas pela LLM.",
        workflow="Ecrã Reimportar — «Incorporar pacote».",
        when="Depois de exportar GET-PACKAGE e editar na LLM.",
        next_step="Prima «Rever alterações» para ver propostas; depois consolidar.",
        concepts=["get_package", "reimport"],
        screen="import",
        confusions=[
            "Não é a secção «Reimportação legada» (fascicle_roundtrip).",
            "Carregar não aplica alterações sem aprovação.",
        ],
        tips=[
            "Importar a partir da Preparação do bloco abre este ecrã automaticamente.",
        ],
    )

    fields["import.get_package_review"] = field(
        "Rever alterações do pacote",
        "Analisa diferenças entre exportação, estado actual e JSON devolvido.",
        "Merge GET-PACKAGE: lista de propostas; consolidação só após decisão humana.",
        "Já importou o pacote correcto para este projecto?",
        purpose="Three-way merge visível antes de tocar na base.",
        workflow="Reimportar — após «Importar pacote».",
        when="Imediatamente após upload bem-sucedido.",
        next_step="Aceitar ou rejeitar cada proposta; depois «Consolidar decisões».",
        concepts=["get_package", "reimport"],
        screen="import",
        confusions=["Fluxo distinto de «Analisar (merge)» do roundtrip legado."],
        tips=["Faça backup crítico antes de consolidar muitas propostas."],
    )

    exch = fields.get("exchange_package") or {}
    exch["short_help"] = "JSON + Markdown para redação — não devolve à app."
    exch["tips"] = [
        "Só para gerar texto na LLM; use GET-PACKAGE se precisa de reimportar.",
        "Grava em exports/; Markdown não é roundtrip.",
    ]
    exch["workflow_context"] = "Preparação do bloco — cartão «GET-LLM (só leitura)»."
    exch["common_confusions"] = [
        "Não é GET-PACKAGE (botão «Exportar pacote» no cartão acima).",
        "Não é o ZIP «Geração LLM» do ecrã Exportar.",
    ]
    fields["exchange_package"] = exch

    rt = fields.get("export.roundtrip") or {}
    rt["label"] = "Roundtrip legado"
    rt["short_help"] = "Mestre/fascículo fascicle_roundtrip — formato avançado."
    rt["definition"] = "Pacotes get_project_master e fascicle-roundtrip com validation.json."
    rt["workflow_context"] = "Ecrã Exportar — cartão «Roundtrip legado»."
    rt["common_confusions"] = [
        "Na maioria dos casos use GET-PACKAGE no cartão acima.",
        "Não é GET-LLM nem exportação estrutural.",
    ]
    rt["tips"] = ["Preferir GET-PACKAGE para um único JSON por fascículo."]
    fields["export.roundtrip"] = rt

    fasc = fields.get("export.fascicle") or {}
    fasc["short_help"] = "Fascículo raiz — atenção ao cartão (GET-PACKAGE vs legado)."
    fasc["definition"] = "Selector partilhado: GET-PACKAGE no cartão dedicado; roundtrip no cartão legado."
    fasc["common_confusions"] = [
        "expFasciclePkg serve GET-PACKAGE; expFascicle serve roundtrip legado.",
    ]
    fasc["tips"] = [
        "Para discussão com retorno: cartão GET-PACKAGE + «Exportar pacote».",
    ]
    fields["export.fascicle"] = fasc

    base = fields.get("export.baseline") or {}
    base["tips"] = [
        "Obrigatória antes de GET-PACKAGE e roundtrip legado.",
        "Não é obrigatória para GET-LLM em camadas (estado live).",
    ]
    base["workflow_context"] = "Ecrã Exportar — cartão Baseline."
    fields["export.baseline"] = base

    se = fields.get("structure_export.overview") or {}
    se["short_help"] = "MD, PDF ou XMind — revisão humana, sem reimportação."
    se["common_confusions"] = [
        "Para devolver alterações à base use GET-PACKAGE, não este export.",
        "Não é GET-LLM nem roundtrip.",
    ]
    se["tips"] = [
        "Útil para reuniões; alterações entram pela Preparação ou GET-PACKAGE.",
    ]
    fields["structure_export.overview"] = se

    llm = fields.get("export.llm_generation") or {}
    llm["common_confusions"] = [
        "Não reimportável — distinto de GET-PACKAGE.",
        "Baseline não é obrigatória (códigos live).",
    ]
    llm["tips"] = [
        "Use quando precisa de mestre + índice + blocos num ZIP para redação.",
    ]
    fields["export.llm_generation"] = llm

    concepts["exchange_package"]["summary"] = "Exportação GET-LLM por bloco (só leitura)."
    concepts["baseline"]["not_this"] = (
        "Não substitui GET-PACKAGE; é pré-requisito para exportações com códigos congelados."
    )
    concepts["block"]["role_in_get"] = (
        "Recipiente de objectivo, âmbito, premissas e pontos; exporta via GET-PACKAGE (ida/volta) ou GET-LLM (leitura)."
    )

    workflows["export_kind_guide"] = [
        {"need": "Devolver alterações da LLM à base (bloco)", "use": "GET-PACKAGE — Preparação do bloco"},
        {"need": "Devolver alterações da LLM à base (fascículo)", "use": "GET-PACKAGE — Ecrã Exportar"},
        {"need": "Gerar texto sem reimportar", "use": "GET-LLM — bloco ou ZIP no ecrã Exportar"},
        {"need": "PDF/MD/XMind para reunião", "use": "Exportar estrutura — não reimportável"},
        {"need": "Formato fascicle_roundtrip antigo", "use": "Roundtrip legado — avançado"},
    ]

    screens["block-editor"]["objective"] = "Definir pontos, premissas e escolher GET-PACKAGE ou GET-LLM."
    screens["block-editor"]["steps"] = [
        "Objectivo e âmbito",
        "Criar pontos ordenados",
        "Marcar ready",
        "Exportar pacote (GET-PACKAGE) ou GET-LLM",
    ]
    screens["block-editor"]["purpose_steps"] = [
        "Definir objetivo e âmbito — enquadrar o bloco.",
        "Criar pontos e premissas — contrato editorial por assunto.",
        "Marcar ready — quando o ponto está exportável.",
        "Exportar pacote (GET-PACKAGE) — discutir na LLM e reimportar.",
        "Ou Exportar GET-LLM — só para gerar texto, sem retorno à app.",
    ]

    screens["export"]["objective"] = "Baseline, GET-PACKAGE, roundtrip legado e GET-LLM."
    screens["export"]["steps"] = [
        "Publicar baseline",
        "GET-PACKAGE por fascículo",
        "Opcional: roundtrip legado ou GET-LLM em ZIP",
    ]
    screens["export"]["audience_note"] = (
        "Quatro saídas no mesmo ecrã: GET-PACKAGE (reimportável), roundtrip legado, GET-LLM (só leitura). "
        "Exportação estrutural MD/PDF está na Estrutura documental."
    )
    screens["export"]["purpose_steps"] = [
        "Baseline — obrigatória para GET-PACKAGE e roundtrip legado.",
        "GET-PACKAGE fascículo — um JSON para discussão e Reimportar.",
        "Roundtrip legado — só se precisa do formato fascicle_roundtrip.",
        "Geração GET-LLM — ZIP para redação; não reimportar.",
    ]

    screens["import"]["objective"] = "Incorporar GET-PACKAGE ou roundtrip legado."
    screens["import"]["steps"] = [
        "Importar pacote GET-PACKAGE",
        "Rever alterações",
        "Consolidar",
    ]
    screens["import"]["purpose_steps"] = [
        "Incorporar pacote — ficheiro GET-PACKAGE devolvido pela LLM.",
        "Rever alterações — merge e lista de propostas.",
        "Consolidar — só o que aprovar entra na base.",
        "Secção legada — fascicle_roundtrip com fascículo no merge.",
    ]

    method["export_decision_summary"] = (
        "GET-PACKAGE = ida e volta (bloco ou fascículo). GET-LLM = leitura para redação. "
        "Estrutura MD/PDF = revisão humana. Roundtrip legado = fascicle_roundtrip avançado."
    )

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", CATALOG, "version", data["catalog_version"])


if __name__ == "__main__":
    main()