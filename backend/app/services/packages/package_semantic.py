"""Heurísticas conceptuais GET-PACKAGE (dry-run F0, não bloqueiam import)."""

from __future__ import annotations


def package_conceptual_warnings(pkg: dict) -> list[str]:
    warnings: list[str] = []
    scope = pkg.get("scope") or {}
    kind = scope.get("kind")
    payload = pkg.get("payload") or {}

    if kind == "block":
        pts = payload.get("development_points") or []
        for i, pt in enumerate(pts):
            lists = pt.get("lists") or {}
            for key in (
                "must_include",
                "limits_and_exclusions",
                "examples",
                "open_questions",
                "questions_to_answer",
            ):
                for j, item in enumerate(lists.get(key) or []):
                    if isinstance(item, str):
                        warnings.append(
                            f"block point[{i}].lists.{key}[{j}]: string solta (esperado objecto tipado)."
                        )
            for key in ("development_guidance", "perspectives", "acceptance_criteria"):
                for j, item in enumerate(lists.get(key) or []):
                    if isinstance(item, dict):
                        warnings.append(
                            f"block point[{i}].lists.{key}[{j}]: objecto (esperado string)."
                        )
        ek = payload.get("editable_knowledge")
        if ek and any(ek.get(b) for b in ("knowledge_items", "decisions", "open_questions")):
            warnings.append(
                "Pacote scope=block mas editable_knowledge preenchido — verificar modo F0 (só conteúdo de bloco)."
            )

    if kind == "fascicle":
        inner = payload
        structure = inner.get("structure") or inner.get("document_structure")
        fascicle = inner.get("fascicle") or {}
        struct_alt = (fascicle.get("structure") or []) if fascicle else []
        if (structure or struct_alt) and (inner.get("development_points") or inner.get("block")):
            warnings.append("Fascículo com estrutura e payload de bloco — risco de modo misto F0.")

    return warnings