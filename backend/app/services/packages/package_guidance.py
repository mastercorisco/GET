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
    "Ler primeiro `rules`, `llm_shapes.collections` e `llm_shapes.anti_patterns`; só depois editar o `payload`.",
    "Alterar apenas conteúdo técnico em campos editáveis; nunca `rules`, `rules_hash`, `schema_version`, `scope`, IDs aprovados, estados nem proveniência.",
    "Bloco: reforçar objectivo do bloco, `development_points` (ideia central, resultado, listas tipadas) e `premises` onde fizer sentido.",
    "Fascículo: trabalhar só em `payload.editable_knowledge` (KI completos); tratar `protected_context` como leitura — não copiar atalhos para editable.",
    "Incerteza ou falta de base documental: criar lacuna (`open_questions` no ponto, ou KI `knowledge_type` open_question); não inventar números, normas ou decisões.",
    "Cumprir tipos de `llm_shapes`: objectos `{text}` ou `{prompt, answer}` nas listas; KI com todas as chaves obrigatórias do exemplo/template.",
    "Estilo: denso e verificável; uma ideia por entrada; sem markdown, comentários ou texto fora do JSON.",
    "Preservar UUID; novos com `new_001`, `new_002`, …; omissão de um nó existente NÃO é eliminação.",
    "Entrega: um único ficheiro JSON GET-PACKAGE 1.0.0 completo, mesmo `export_id`; pode omitir `llm_brief` na devolução.",
]

BRIEF_READ_ORDER: list[str] = [
    "`rules` (7 regras) — contrato inviolável.",
    "`llm_shapes.anti_patterns` e `collection_priority` — evita rejeição no importador.",
    "`llm_shapes.collections` — forma exacta de cada array/objecto editável.",
    "`payload` — aplicar alterações; comparar com `sample_from_export` quando existir.",
]

BRIEF_WORKFLOW: list[str] = [
    "Mapear o que está incompleto ou vago no payload (pontos, listas, KI).",
    "Enriquecer campo a campo, respeitando tipos; consolidar dúvidas em open_question em vez de preencher à sorte.",
    "Validar mentalmente cada lista contra o `item_template` ou `sample_from_export` da respectiva path.",
    "Rever anti-padrões; garantir envelope completo e `export_id` inalterado.",
    "Responder só com o JSON final (ficheiro ou bloco de código JSON único, sem explicação fora do ficheiro).",
]

BRIEF_SELF_CHECK: list[str] = [
    "`rules_hash` e `rules` iguais ao ficheiro recebido?",
    "Alguma lista com strings soltas ou `lists: {}`?",
    "Knowledge items sem estrutura completa (só title/content)?",
    "Campos inventados (ex. node_id, question) em KI?",
    "Mesmo `export_id` e todas as secções obrigatórias presentes?",
]

SCOPE_TASK_FOCUS: dict[str, str] = {
    "block": (
        "Foco: `payload.objective`, `development_points[]` e `premises[]`. "
        "Em cada ponto, manter todas as chaves de `lists` com tipos correctos."
    ),
    "fascicle": (
        "Foco: `payload.editable_knowledge` (knowledge_items, decisions, open_questions). "
        "Não alterar itens em `protected_context` excepto se a regra do pacote o permitir explicitamente."
    ),
}

USER_CONTRIBUTION_HINTS: list[str] = [
    "Objectivo desta sessão (ex.: «aprofundar pontos ready sem novos requisitos»).",
    "Âmbito: IDs/títulos dos pontos ou KI que PODE tocar; o que é intocável.",
    "Decisões já fechadas (com referência D-xx ou título da decisão).",
    "Terminologia obrigatória e o que evitar (siglas, sinónimos).",
    "Profundidade desejada (esboço vs texto quase final) e limite de volume.",
]

USER_CONTRIBUTION_TEMPLATE = """\
Objectivo desta sessão: [ex. enriquecer pontos ready / fechar open_questions do fascículo]

Pode alterar: [pontos ou KI concretos, ou «todos os draft/ready»]
Não alterar: [premissas aprovadas, decisões D-xx, protected_context, etc.]

Decisões fechadas: [lista ou «nenhuma nova»]
Terminologia: [glossário, nomes de sistemas, «adjudicatário» vs «contractual»]
Tom e profundidade: [técnico conciso / ~N palavras por item / sem valores numéricos inventados]
"""