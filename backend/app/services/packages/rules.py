from __future__ import annotations

import hashlib
import json

CANONICAL_RULES: list[str] = [
    "Preservar todos os identificadores (UUID) existentes sem alteração.",
    "Não inventar parâmetros técnicos, valores ou requisitos sem base no pacote.",
    "Omissão de um objeto no JSON devolvido não significa eliminação na base.",
    "Não alterar aprovação, ciclo de vida, maturidade nem proveniência.",
    "Novos objetos devem usar identificadores temporários new_001, new_002, etc.",
    "Devolver o ficheiro JSON completo, sem truncar nem omitir secções obrigatórias.",
    "Remoções só mediante proposta explícita no payload, nunca por omissão.",
]


def rules_hash() -> str:
    canonical = json.dumps(CANONICAL_RULES, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()