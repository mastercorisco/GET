"""Textos partilhados entre llm_shapes e llm_brief (envelope GET-PACKAGE)."""

from __future__ import annotations

PACKAGE_ANTI_PATTERNS: list[str] = [
    "Não usar campos fora do schema (ex.: node_id, question isolado) em knowledge items.",
    "Não devolver knowledge items só com title/content — usar knowledge-item.schema.json completo.",
    "Não colocar strings em must_include, open_questions ou questions_to_answer; usar {text} ou {prompt, answer}.",
    "Não devolver lists vazio {} — manter todas as chaves de lists em cada development_point.",
    "Não alterar rules, rules_hash, schema_version nem omitir secções do envelope sem devolver o pacote completo.",
]

COLLECTION_PRIORITY = (
    "Preferir sample_from_export a item_template quando existir no llm_shapes. "
    "item_template é molde vazio — preencher, não devolver igual."
)

CANONICAL_BRIEF_OBJECTIVES: list[str] = [
    "Enriquecer apenas campos editáveis do payload, com conteúdo técnico denso e fundamentado.",
    "O que não souber: registar em open_questions (bloco) ou knowledge_type open_question (fascículo); não inventar.",
    "Seguir llm_shapes.collections (tipos e item_template) e anti_patterns.",
    "Texto conciso por item; evitar prosa longa fora dos campos previstos.",
    "Preservar UUID existentes; novos objetos com new_001, new_002, …",
    "Omissão no JSON devolvido não elimina conteúdo aprovado na base.",
    "Devolver o ficheiro GET-PACKAGE completo com o mesmo export_id.",
]

USER_CONTRIBUTION_HINTS: list[str] = [
    "Âmbito: que blocos/fascículos ou pontos pode alterar.",
    "Decisões já fechadas que não devem ser revertidas.",
    "Terminologia obrigatória (ex.: contratação, adjudicatário).",
    "Prioridades desta sessão e o que fica explicitamente fora.",
]