"""Heurísticas de template_id para pontos (CTBJ)."""


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