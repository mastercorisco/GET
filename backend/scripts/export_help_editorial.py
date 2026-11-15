"""Exporta textos de ajuda para edição externa (get_help_editorial.pt-PT.json)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalogs" / "get_help_catalog.pt-PT.json"
OUT = ROOT / "catalogs" / "get_help_editorial.pt-PT.json"
SHELL = ROOT / "backend" / "app" / "static" / "index.html"

HELP_KEY_RE = re.compile(r'data-help-key="([^"]+)"')

FIELD_EDITABLE = (
    "label",
    "short_help",
    "definition",
    "guiding_question",
    "instructions",
    "purpose_in_app",
    "workflow_context",
    "when_to_use",
    "what_happens_next",
    "common_confusions",
    "tips",
    "good_examples",
    "bad_examples",
)

FIELD_PROTECTED = ("related_concepts", "related_screen", "allow_use_example")

GROUP_ORDER = [
    "workspace",
    "settings",
    "library",
    "workbook",
    "project",
    "document",
    "technical",
    "block",
    "premise",
    "development_point",
    "export",
    "import",
    "backup",
    "knowledge",
    "other",
]

GROUP_LABELS = {
    "workspace": "Workspace e arranque",
    "settings": "Configurações (aparência)",
    "library": "Biblioteca EDA",
    "workbook": "Modelo Excel",
    "project": "Projeto",
    "document": "Estrutura documental",
    "technical": "Árvore técnica",
    "block": "Preparação do bloco",
    "premise": "Premissas",
    "development_point": "Pontos de desenvolvimento",
    "export": "Exportar para LLM",
    "import": "Reimportar",
    "backup": "Backups",
    "knowledge": "Conhecimento",
    "other": "Outros",
}


def _group(key: str) -> str:
    prefix = key.split(".", 1)[0]
    return prefix if prefix in GROUP_LABELS else "other"


def _priority(key: str, in_shell: bool) -> str:
    if in_shell:
        return "critical"
    if key.startswith("development_point."):
        return "high"
    if key.startswith(("block.", "premise.", "export.", "import.")):
        return "high"
    return "normal"


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    shell_keys = set(HELP_KEY_RE.findall(SHELL.read_text(encoding="utf-8")))
    shell_keys.update(k for k in catalog.get("fields", {}) if k.startswith("development_point."))

    fields_out: dict[str, dict] = {}
    by_group: dict[str, list[str]] = {g: [] for g in GROUP_ORDER}

    for key, entry in sorted(catalog.get("fields", {}).items()):
        grp = _group(key)
        by_group.setdefault(grp, []).append(key)
        in_shell = key in shell_keys
        editable = {f: entry.get(f) for f in FIELD_EDITABLE if f in entry or f in FIELD_EDITABLE}
        for f in FIELD_EDITABLE:
            if f not in editable:
                editable[f] = [] if f in ("common_confusions", "tips", "good_examples", "bad_examples") else ""
        protected = {f: entry.get(f) for f in FIELD_PROTECTED if f in entry}
        fields_out[key] = {
            "group": grp,
            "priority": _priority(key, in_shell),
            "in_shell": in_shell,
            "surfaces": (
                ["index.html"] if in_shell and key in shell_keys and not key.startswith("development_point.")
                else []
            )
            + (["block_card"] if key.startswith("development_point.") else []),
            "editable": editable,
            "protected": protected,
        }

    field_order = []
    for g in GROUP_ORDER:
        field_order.extend(sorted(by_group.get(g, [])))

    editorial = {
        "document_type": "get_help_editorial",
        "editorial_version": "1.0.0",
        "locale": catalog.get("locale", "pt-PT"),
        "source_catalog_version": catalog.get("catalog_version"),
        "exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workflow": {
            "purpose": (
                "Ficheiro para revisão de textos fora do repositório (Word, folha de cálculo, revisão humana). "
                "Edite sobretudo os blocos em fields.*.editable e as secções concepts, method, screens, workflows."
            ),
            "import_command": "python backend/scripts/import_help_editorial.py",
            "do_not_change": [
                "document_type",
                "Chaves de fields (ex.: development_point.title)",
                "protected.related_concepts e related_screen sem validar o catálogo",
            ],
            "quality_bar": [
                "purpose_in_app: para que serve no GET, em linguagem para quem não conhece o produto",
                "workflow_context: onde encaixa na jornada workspace → biblioteca → bloco → export",
                "when_to_use / what_happens_next: decisão do utilizador e efeito após gravar",
                "common_confusions: erros reais de quem vem do Word ou da LLM",
                "definition/guiding_question: precisão técnica; exemplos concretos de EDA quando possível",
            ],
        },
        "groups": GROUP_LABELS,
        "field_order": field_order,
        "fields": fields_out,
        "concepts": catalog.get("concepts", {}),
        "method": catalog.get("method", {}),
        "screens": {
            sid: {
                k: s[k]
                for k in (
                    "title",
                    "objective",
                    "audience_note",
                    "purpose_steps",
                    "steps",
                    "empty_state",
                    "next",
                )
                if k in s
            }
            for sid, s in (catalog.get("screens") or {}).items()
        },
        "workflows": catalog.get("workflows", {}),
    }

    OUT.write_text(json.dumps(editorial, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", OUT, "fields", len(fields_out))


if __name__ == "__main__":
    main()