"""Textos partilhados entre llm_shapes e llm_brief (envelope GET-PACKAGE)."""

from __future__ import annotations

PACKAGE_ANTI_PATTERNS: list[str] = [
    "Knowledge item só com title/content ou campos inventados (node_id, question, tags soltas).",
    "Strings soltas em must_include, limits_and_exclusions, examples, open_questions ou questions_to_answer — usar objectos com as chaves do schema ({text} ou {prompt, answer}).",
    "Objectos em development_guidance, perspectives ou acceptance_criteria — estas listas são arrays de strings.",
    "lists omitido, {} incompleto, ou chaves de lists em falta num development_point.",
    "Alterar rules, rules_hash, schema, schema_version, scope, export_id ou truncar o envelope.",
    "Copiar protected_context para editable_knowledge sem estrutura KI completa e UUID/new_* correcto.",
    "Valores técnicos (dimensões, classes, artigos de norma) sem base no pacote — usar open_question em vez disso.",
]

COLLECTION_PRIORITY = (
    "Preferir sample_from_export a item_template quando existir no llm_shapes. "
    "item_template é molde vazio — preencher com conteúdo novo, nunca devolver igual."
)

BRIEF_OUTPUT_CONTRACT: list[str] = [
    "Uma única resposta: ficheiro JSON GET-PACKAGE 1.0.x parseável (sem texto antes/depois).",
    "Mesmo export_id, rules e rules_hash byte-a-byte iguais ao ficheiro recebido.",
    "Todos os UUID existentes preservados; criações só com new_001, new_002, …",
    "Omissão de um elemento existente NÃO apaga dados na app — se quiser remover, isso é fluxo humano, não omissão silenciosa.",
]

CANONICAL_BRIEF_OBJECTIVES: list[str] = [
    "Ler rules → llm_shapes.anti_patterns → llm_shapes.collections → payload (nesta ordem).",
    "Editar só conteúdo técnico em campos permitidos; zero alterações em metadados, estados, aprovação e proveniência.",
    "Bloco: objective, development_points (core_idea, intended_outcome, lists tipadas) e premises coerentes entre si.",
    "Fascículo: apenas editable_knowledge.* com KI schema-completos; protected_context é referência, não atalho de cópia.",
    "Cada entrada de lista: uma ideia verificável; must_include = obrigação traceável; open_questions = lacuna honesta.",
    "Na dúvida: open_question (ponto ou KI) com prompt claro; nunca preencher com suposição ou número inventado.",
    "Densidade: frases curtas; evitar redundância entre core_idea, must_include e questions_to_answer.",
    "Devolver envelope completo; llm_brief e llm_shapes podem omitir-se na devolução.",
]

BRIEF_QUALITY_CRITERIA: list[str] = [
    "Cada ponto alterado fica autónomo: quem lê core_idea + intended_outcome percebe o que muda no documento final.",
    "must_include refere requisitos ou factos que o texto gerado terá de respeitar (não generalidades vazias).",
    "open_questions formulam o que falta decidir ou confirmar, com contexto suficiente para um humano responder.",
    "Knowledge items (fascículo): title inequívoco; content com raciocínio compacto; knowledge_type alinhado ao papel do item.",
]

BRIEF_READ_ORDER: list[str] = [
    "rules — as 7 regras são o contrato legal do ficheiro.",
    "llm_shapes.anti_patterns + collection_priority — erros que invalidam o import.",
    "llm_shapes.collections — path, tipos, sample_from_export / item_template por lista.",
    "payload — aplicar mudanças; validar cada array contra o shape da path correspondente.",
]

BRIEF_WORKFLOW: list[str] = [
    "Inventariar lacunas: campos vazios, listas só com molde, KI incompletos, texto genérico.",
    "Por ponto/KI: reescrever o mínimo necessário; propagar consistência terminológica no mesmo bloco/fascículo.",
    "Para cada lista editada, verificar element_kind em llm_shapes (strings vs objectos).",
    "Passar checklist de autoverificação; confirmar rules_hash inalterado.",
    "Entregar só o JSON (recomendado: anexar como ficheiro .json; se usar código, um bloco ```json único).",
]

BRIEF_SELF_CHECK: list[str] = [
    "rules e rules_hash idênticos ao input?",
    "export_id e schema_version intactos?",
    "Todas as chaves de lists presentes em cada development_point?",
    "Listas objecto (must_include, open_questions, …) sem strings soltas; listas string (development_guidance, …) sem objectos?",
    "KI com knowledge_type, revision, states, provenance, edit_policy (não só title/content)?",
    "Envelope completo (payload + scope + rules + export_id no mínimo)?",
]

BRIEF_SHAPE_EXAMPLES: dict[str, list[str]] = {
    "block": [
        "BOM must_include: {\"text\": \"O texto gerado deve explicitar o critério de aceitação X sem valores numéricos novos.\"}",
        "MAU must_include: \"incluir requisitos de segurança\" (string — rejeitado).",
        "BOM open_questions no ponto: {\"prompt\": \"Qual o tempo máximo aceitável para …?\", \"answer\": \"\"}",
        "BOM development_guidance: \"Explicitar critério X sem inventar valores.\" (string)",
        "MAU development_guidance: {\"text\": \"…\"} (objecto — rejeitado).",
        "BOM listas: manter todas as chaves de lists (mesmo arrays vazios).",
    ],
    "fascicle": [
        "BOM novo open_question em editable_knowledge: KI completo com knowledge_type open_question e content que explica a lacuna.",
        "MAU: {\"title\": \"Pergunta\", \"content\": \"?\"} sem resto do schema.",
        "BOM decisão: knowledge_type decision; content resume o que ficou fechado e o impacto no fascículo.",
    ],
}

SCOPE_TASK_FOCUS: dict[str, str] = {
    "block": (
        "Prioridade: development_points com status draft/ready — alinhar core_idea, intended_outcome e listas. "
        "objective do bloco só se estiver incoerente com os pontos. premises: rever ligação aos pontos tocados."
    ),
    "fascicle": (
        "Prioridade: editable_knowledge.open_questions e decisions em falta; depois knowledge_items editáveis. "
        "Não reescrever protected_context; usar-no só para tom e terminologia."
    ),
}

USER_CONTRIBUTION_HINTS: list[str] = [
    "Resultado esperado: o que deve estar melhor no JSON após a sessão.",
    "Âmbito positivo (pode) e negativo (não) — seja concreto (títulos de pontos, IDs, decisões).",
    "Factos assumidos como verdade nesta sessão (glossário, interfaces, decisões D-xx).",
    "Conversa: o que a LLM perguntar e tu responderes regista como decidido (contributo e JSON); não reabrir como lacuna.",
    "Profundidade: esboço / quase-final; limites de volume por campo.",
]

USER_CONTRIBUTION_TEMPLATE = """\
## Resultado esperado desta sessão
[Ex.: pontos ready com must_include e open_questions credíveis; ou fechar lacunas do fascículo sem novos KI]

## Âmbito
Pode alterar: [ex. todos os development_points draft/ready deste bloco / só «Ponto 3 — …»]
Não alterar: [ex. premissas approved; objective; pontos archived]
Não criar: [ex. novos pontos; novos KI fora de editable_knowledge]

## Factos e decisões que a LLM deve tratar como fechados
- [Decisão D-xx ou frase explícita]
- [Terminologia obrigatória: adjudicatário, ESF, …]
- O que ficar acordado na conversa (respostas a perguntas da LLM) trata como decidido — reflectir no JSON (ex. `open_question.answer` ou decisão explícita), não como nova lacuna.

## Prioridades (ordem)
1. [ex. open_questions honestas antes de inventar requisitos]
2. [ex. must_include verificáveis]
3. [ex. core_idea alinhada ao intended_outcome]

## Tom e limites
Idioma: pt-PT, técnico, conciso. Sem valores numéricos ou referências normativas novas sem open_question.

## Aceitação
Devolução deve importar na app GET sem erro; rules_hash inalterado; mesmo export_id.
"""