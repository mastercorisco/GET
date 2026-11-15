"""Atualiza get_help_catalog.pt-PT.json para v1.3.0 (Método GET, merge forçado)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalogs" / "get_help_catalog.pt-PT.json"
TEMPLATES = ROOT / "catalogs" / "development_point_templates.pt-PT.json"

GENERIC_PREFIX = re.compile(r"^No GET, este campo «")

METHOD = {
    "title": "Método GET",
    "principle": (
        "Três actividades separadas: (1) estruturar conhecimento no GET, "
        "(2) desenvolver texto numa LLM externa, (3) validar tecnicamente o resultado. "
        "O GET controla o input autoritativo; a LLM não é autoridade técnica."
    ),
    "flow_steps": [
        "Utilizador de engenharia",
        "GET (estrutura, validação, exportação)",
        "JSON canónico",
        "LLM externa (redação)",
        "Revisão humana",
        "Reimportação controlada (opcional)",
    ],
    "hierarchy_summary": (
        "Biblioteca (KnowledgeItem) → Projeto → Fascículo → Bloco → Ponto de desenvolvimento"
    ),
    "governance_rules": [
        "O utilizador é a autoridade técnica.",
        "A LLM não cria decisões aprovadas.",
        "Questões pendentes permanecem visíveis.",
        "Exemplos não são requisitos.",
        "Orientações de redação não são premissas.",
        "Premissas não ocultam requisitos.",
        "Conteúdo aprovado alterado exige revisão.",
        "Exportações rastreáveis por ID e versão.",
        "Importações validadas antes de aplicação.",
        "Omissão no JSON importado não é eliminação.",
    ],
    "exchange_semantics": {
        "authoritative_content": (
            "Objectivo, premissas, pontos, ideias centrais, obrigatórios, limites e critérios — "
            "o que a LLM deve respeitar sem inventar."
        ),
        "supporting_context": (
            "KnowledgeItems e referências ligadas: ajudam a compreender, "
            "sem promover automaticamente a requisito."
        ),
        "unresolved_matters": (
            "Questões pendentes e informação em falta — a LLM não pode fechar silenciosamente."
        ),
        "generation_instructions": (
            "Ordem dos pontos, idioma, tom, liberdade configurada; sugestões separadas do conteúdo aprovado."
        ),
    },
    "help_system_note": (
        "Ajuda em get_help_catalog.pt-PT.json: níveis essential / normal / detailed; "
        "popup (i) com narrativa GET; painel de preparação do bloco expõe este método. Ver docs/GET_METHOD.md."
    ),
    "example_walkthrough": (
        "Bloco «Controladores locais»: ponto sobre perda de referências remotas com ideia central, "
        "orientações, premissas, obrigatórios, limites e critério que proíbe valores não aprovados."
    ),
}

CONCEPTS_V13 = {
    "block": {
        "label": "Bloco",
        "summary": "Unidade de preparação documental (ex. F04_B03).",
        "role_in_get": "Recipiente de objectivo, âmbito, premissas e pontos antes do pacote exchange. Não é texto Word nem resposta da LLM.",
        "not_this": "Não é o capítulo redigido; são inputs estruturados para desenvolvimento externo.",
    },
    "development_point": {
        "label": "Ponto de desenvolvimento",
        "summary": "Assunto a desenvolver por ordem, com condições.",
        "role_in_get": "Contrato por tema: ideia central, listas e critérios. A LLM redige fora do GET; o utilizador controla criação e ordem.",
        "not_this": "Não é KnowledgeItem (conhecimento já possuído) nem parágrafo final do caderno.",
    },
    "knowledge_item": {
        "label": "Unidade de conhecimento",
        "summary": "Conhecimento reutilizável da biblioteca ou do projecto.",
        "role_in_get": "Factos, requisitos, decisões com identidade e revisão. Liga-se a blocos/pontos por referência, sem duplicar corpo.",
        "not_this": "Não é um DevelopmentPoint (pedido de redação para um bloco).",
    },
    "premise": {
        "label": "Premissa",
        "summary": "Condição assumida verdadeira para enquadrar.",
        "role_in_get": "Pode existir em projecto, fascículo, bloco ou ponto; exportação reúne sem copiar em cada ponto.",
        "not_this": "Não é requisito ao adjudicatário («deve»).",
    },
    "reference": {
        "label": "Referência",
        "summary": "Fonte citável (norma, manual, decisão).",
        "role_in_get": "Biblioteca global; ligações em exportações como suporte.",
        "not_this": "Não substitui o texto técnico escrito ou desenvolvido.",
    },
    "open_question": {
        "label": "Questão pendente",
        "summary": "Lacuna que exige decisão humana.",
        "role_in_get": "Visível no pacote em unresolved_matters; impede que a LLM assuma resposta.",
        "not_this": "Não é premissa confirmada nem requisito fechado.",
    },
    "workspace": {
        "label": "Workspace",
        "summary": "Pasta local com SQLite e exports.",
        "role_in_get": "Separa dados do código da app; um workspace = projectos e backups nesta máquina.",
        "not_this": "Não é o repositório Git do GET.",
    },
    "baseline": {
        "label": "Baseline",
        "summary": "Marco aprovado antes de exportações mestres.",
        "role_in_get": "Fixa revisões para exportações reproduzíveis do projecto/fascículo.",
        "not_this": "Não é o pacote exchange por bloco na Preparação.",
    },
    "exchange_package": {
        "label": "Pacote exchange",
        "summary": "JSON por bloco para a LLM externa.",
        "role_in_get": "Sai da Preparação do bloco; contrato get_exchange_package.schema.json.",
        "not_this": "Não é export mestre nem ficheiro Word.",
    },
    "project": {
        "label": "Projeto",
        "summary": "Empreitada ou especificação concreta.",
        "role_in_get": "Contexto comum: instalação, âmbito, premissas transversais, fascículos e conhecimento específico.",
        "not_this": "Não é só uma pasta no disco — é entidade na base com ciclo de vida.",
    },
    "fascicle": {
        "label": "Fascículo",
        "summary": "Grande domínio do caderno (F04, etc.).",
        "role_in_get": "Agrupa blocos ordenados; ID interno estável quando a ordem muda.",
        "not_this": "Não é um ficheiro PDF; é nó da árvore documental.",
    },
    "authoritative_content": {
        "label": "Conteúdo autoritativo",
        "summary": "Parte do JSON que a LLM deve respeitar.",
        "role_in_get": "Inclui ideias centrais, obrigatórios, limites e critérios exportados.",
        "not_this": "Não inclui sugestões exploratórias não aprovadas.",
    },
    "supporting_context": {
        "label": "Contexto de suporte",
        "summary": "Material de compreensão no pacote.",
        "role_in_get": "KnowledgeItems e referências ligadas; não promovidos automaticamente a requisito.",
        "not_this": "Não é texto livre para a LLM alterar como requisito.",
    },
    "unresolved_matters": {
        "label": "Assuntos em aberto",
        "summary": "Questões pendentes e lacunas explícitas.",
        "role_in_get": "Força a LLM a não resolver silenciosamente decisões em falta.",
        "not_this": "Não são orientações de redação.",
    },
    "generation_instructions": {
        "label": "Instruções de geração",
        "summary": "Regras de processamento para a LLM.",
        "role_in_get": "Ordem, idioma, não inventar requisitos, separar sugestões.",
        "not_this": "Não substituem a ideia central de cada ponto.",
    },
    "reimport": {
        "label": "Reimportação",
        "summary": "Entrada de JSON devolvido pela LLM.",
        "role_in_get": "Staging + merge three-way + aprovação por proposta; nunca consolidação automática.",
        "not_this": "Não é importação de Word ou Markdown como roundtrip.",
    },
    "validation": {
        "label": "Validação",
        "summary": "Alertas concretos no bloco e nos pontos.",
        "role_in_get": "Informação, aviso ou problema; sem pontuação abstracta de qualidade.",
        "not_this": "Não bloqueia rascunho de trabalho excepto operações inválidas (ex. export sem título).",
    },
    "development_point_template": {
        "label": "Modelo estrutural",
        "summary": "Esqueleto de prompts para novo ponto.",
        "role_in_get": "Catálogo development_point_templates.pt-PT.json; cria listas vazias, não decisões.",
        "not_this": "Não preenche requisitos nem valores técnicos.",
    },
}

WORKFLOWS = {
    "user_controls": [
        "Que assuntos desenvolver",
        "A ordem dos assuntos",
        "As ideias nucleares a preservar",
        "As premissas e o nível de confiança",
        "O que é obrigatório no texto",
        "O que é proibido assumir",
        "As referências e conhecimento ligados",
        "As lacunas visíveis para a LLM",
        "Os critérios de aceitação do resultado",
    ],
    "llm_role": (
        "A LLM transforma a estrutura autoritativa em texto desenvolvido; "
        "não escolhe o conteúdo do bloco nem aprova decisões."
    ),
    "method_llm_boundaries": [
        "Não inventar requisitos não presentes nos inputs.",
        "Não resolver questões pendentes sem decisão humana.",
        "Não promover exemplos ou contexto de suporte a requisito.",
        "Separar sugestões exploratórias do conteúdo aprovado.",
    ],
    "example_walkthrough": METHOD["example_walkthrough"],
}

SCREEN_EXTRA = {
    "project": {
        "audience_note": "O projecto é o contexto da obra — premissas aqui aplicam-se a todos os fascículos sem copiar em cada bloco.",
        "purpose_steps": [
            "Criar ou activar projecto — para isolar dados e exportações por caderno.",
            "Registar conhecimento específico — quando difere da biblioteca EDA comum.",
            "Avançar para estrutura documental — fascículos e blocos.",
        ],
    },
    "workbook": {
        "audience_note": "O Excel valida estrutura de requisitos legados; não substitui o método de pontos no GET.",
        "purpose_steps": [
            "Validar ficheiro — relatório sem importação automática para o SQLite.",
            "Usar como referência — conhecimento estruturado entra via biblioteca ou projecto.",
        ],
    },
    "project-technical": {
        "audience_note": "Árvore técnica (sistemas, funções) complementa a árvore documental; ambas podem exportar.",
        "purpose_steps": [
            "Registar instâncias — para ligações técnicas reutilizáveis.",
            "Manter hierarquia — pai/filho sem confundir com fascículos.",
        ],
    },
    "backups": {
        "audience_note": "Backups protegem a base SQLite do workspace; distinto de baseline de revisão.",
        "purpose_steps": [
            "Criar backup antes de alterações grandes — cópia recuperável do get.db.",
            "Restaurar só com consciência — substitui o estado local do workspace.",
        ],
    },
    "diagnostics": {
        "audience_note": "Diagnóstico local para suporte; não expõe dados para a cloud.",
        "purpose_steps": [
            "Rever mensagens — integridade da instalação e caminhos.",
            "Corrigir workspace ou permissões — antes de exportações críticas.",
        ],
    },
    "block-editor": {
        "audience_note": (
            "Aqui define instruções para a LLM; o GET não escreve o caderno. "
            "Cada ponto é um cartão recolhível com secções independentes (§ método)."
        ),
        "purpose_steps": [
            "Objectivo e âmbito — enquadram o capítulo no pacote JSON.",
            "Premissas e pontos ordenados — contrato do que a LLM pode e não pode inventar.",
            "Painel de preparação à direita — método, conceitos, validação e exportação exchange.",
            "Validação e exportar pacote — ficheiro para a LLM externa.",
        ],
    },
}

DEV_POINT_FORCE: dict[str, dict[str, object]] = {
    "development_point.title": {
        "purpose_in_app": "Nomeia o assunto no índice do bloco e no JSON; não substitui a ideia central técnica.",
        "workflow_context": "Cartão do ponto na Preparação do bloco, antes de exportar o pacote exchange.",
        "when_to_use": "Ao criar ou renomear um ponto; mantenha curto e específico.",
        "what_happens_next": "Aparece ordenado na exportação; a LLM desenvolve cada título em sequência.",
        "related_concepts": ["development_point", "block"],
        "common_confusions": ["Colocar o requisito completo no título.", "Título genérico tipo «SCADA»."]},
    "development_point.core_idea": {
        "purpose_in_app": "Afirmação técnica autoritativa que a LLM deve preservar — âncora do ponto.",
        "workflow_context": "Primeira secção substantive do cartão expandido.",
        "when_to_use": "Sempre; é o campo mais crítico do método.",
        "what_happens_next": "Entra em authoritative_content no JSON; validação alerta tarefas de redação disfarçadas.",
        "related_concepts": ["development_point", "authoritative_content"],
        "common_confusions": [
            "«Explicar X» em vez de afirmação técnica.",
            "Misturar vários requisitos independentes numa frase."]},
    "development_point.intended_outcome": {
        "purpose_in_app": "Estado de compreensão esperado após leitura do texto desenvolvido.",
        "workflow_context": "Após ideia central no cartão.",
        "when_to_use": "Quando o resultado esperado não é óbvio só pela ideia central.",
        "related_concepts": ["development_point"],
        "common_confusions": ["Lista de tarefas em vez de conclusão para o leitor."]},
    "development_point.development_guidance": {
        "purpose_in_app": "Como estruturar ou relacionar o assunto — sem esconder requisitos aqui.",
        "workflow_context": "Secção Orientações; uma ideia por item na lista.",
        "when_to_use": "Quando precisa de ênfases (funcional vs operacional, falhas, etc.).",
        "related_concepts": ["development_point"],
        "common_confusions": ["Requisito «deve» numa orientação — use Elementos obrigatórios."]},
    "development_point.premises": {
        "purpose_in_app": "Condições assumidas verdadeiras para este ponto (além das herdadas do projecto/bloco).",
        "workflow_context": "Secção Premissas do cartão; exportação inclui nível e confiança.",
        "when_to_use": "Pressupostos de projeto, normas ou decisões aplicáveis só a este assunto.",
        "related_concepts": ["premise", "development_point"],
        "common_confusions": ["Usar premissa para exigir solução ao adjudicatário."]},
    "development_point.must_include": {
        "purpose_in_app": "Matéria que tem de constar no desenvolvimento — contrato explícito.",
        "workflow_context": "Secção Obrigatórios; um item por linha.",
        "when_to_use": "Elementos não negociáveis (deteção, sinalização, fallback, etc.).",
        "related_concepts": ["development_point", "authoritative_content"],
        "common_confusions": ["Duplicar o mesmo item como limite e obrigatório sem motivo."]},
    "development_point.limits_and_exclusions": {
        "purpose_in_app": "Protecção contra invenção: o que não definir, assumir ou incluir.",
        "workflow_context": "Secção Limites; tipos: não definir, fora do âmbito, remeter a detalhe.",
        "when_to_use": "Evitar que a LLM fixe valores ou marcas não aprovados.",
        "related_concepts": ["development_point", "authoritative_content"],
        "common_confusions": ["Limite vago sem alternativa (preferir questão pendente)."]},
    "development_point.questions_to_answer": {
        "purpose_in_app": (
            "Perguntas que o desenvolvimento deve responder explicitamente; "
            "na UI também liga IDs de conhecimento/referência nesta secção."
        ),
        "workflow_context": "Secção Conhecimento e referências / listas de perguntas.",
        "when_to_use": "Questões obrigatórias (o quê desencadeia, como sinaliza, recuperação).",
        "related_concepts": ["development_point", "knowledge_item", "reference"],
        "common_confusions": [
            "Confundir perguntas a responder com questões pendentes (ainda sem resposta).",
            "Tratar ID de biblioteca como texto a redigir."]},
    "development_point.open_questions": {
        "purpose_in_app": "Decisões em falta que a LLM não pode fechar sozinha.",
        "workflow_context": "Secção Questões pendentes → unresolved_matters na exportação.",
        "when_to_use": "TBD, «confirmar com cliente», escolhas não fechadas.",
        "related_concepts": ["open_question", "unresolved_matters"],
        "common_confusions": ["Esconder incerteza numa premissa de confiança alta."]},
    "development_point.acceptance_criteria": {
        "purpose_in_app": "Como verificar se o texto desenvolvido respeitou os inputs.",
        "workflow_context": "Secção Critérios; antes de marcar ready/approved.",
        "when_to_use": "Sempre que a revisão humana pós-LLM precisa de checklist.",
        "related_concepts": ["development_point", "validation"],
        "common_confusions": ["Critério que repete só a ideia central sem verificável."]},
    "development_point.llm_freedom": {
        "purpose_in_app": (
            "strict: só o fornecido; bounded: clareza sem novos requisitos; "
            "exploratory: sugestões separadas. Recomendado strict em cadernos."
        ),
        "workflow_context": "Secção Estado e LLM do cartão; incluído nas generation_instructions.",
        "when_to_use": "Por defeito strict; bounded para texto mais didático; exploratory só com revisão rigorosa.",
        "related_concepts": ["development_point", "generation_instructions"],
        "common_confusions": ["exploratory para requisitos contratuais sem revisão."]},
    "development_point.status": {
        "purpose_in_app": (
            "draft/incomplete: trabalho; ready: exportável com mínimos; approved: inputs validados; "
            "obsolete: histórico. Não confundir com aprovação do texto da LLM."
        ),
        "workflow_context": "Secção Estado e LLM; exportação inclui ready/approved, draft opcional.",
        "when_to_use": "Actualizar quando o ponto ganha lacunas resolvidas ou conteúdo mínimo.",
        "related_concepts": ["development_point", "validation", "exchange_package"],
        "common_confusions": ["Marcar approved só porque a LLM devolveu texto."]},
    "development_point.overview": {
        "purpose_in_app": "Visão do cartão: um ponto é o contrato de desenvolvimento de um assunto no bloco.",
        "workflow_context": "Ajuda ao expandir o primeiro ponto na Preparação do bloco.",
        "when_to_use": "Quando começa a usar pontos ou precisa de rever o método.",
        "related_concepts": ["development_point", "block", "knowledge_item"],
        "common_confusions": ["Confundir ponto com unidade de conhecimento da biblioteca."]},
    "development_point.perspectives": {
        "label": "Perspectivas",
        "short_help": "Dimensões a considerar no desenvolvimento (funcional, segurança, etc.).",
        "definition": "Assinala ângulos técnicos que o texto deve cobrir, sem substituir orientações ou obrigatórios.",
        "guiding_question": "Que dimensões devem ser consideradas?",
        "instructions": "Seleccione as relevantes; exportadas no ponto quando preenchidas.",
        "good_examples": ["operational", "availability", "cybersecurity"],
        "bad_examples": [],
        "tips": ["Não use perspectiva como substituto de requisito."],
        "allow_use_example": False,
        "purpose_in_app": "Garante que a LLM considera dimensões (operação, cibersegurança, ensaios, etc.).",
        "workflow_context": "Campo do ponto na exportação JSON (UI de edição em evolução).",
        "when_to_use": "Assuntos multidisciplinares ou quando falta um ângulo na revisão.",
        "related_concepts": ["development_point"],
        "related_screen": "block-editor",
        "common_confusions": ["Perspectiva vazia com tudo nas orientações — ok, mas menos filtrável."]},
}

FAMILY_FORCE: dict[str, dict[str, object]] = {
    "project.template_version": {
        "purpose_in_app": "Versão do modelo de projecto usada ao criar — rastreio e compatibilidade.",
        "workflow_context": "Ecrã Projecto, ao criar nova empreitada.",
        "when_to_use": "Ao criar projecto; alinhar com templates aprovados pela equipa.",
        "related_concepts": ["project"],
        "related_screen": "project"},
    "project.name": {
        "purpose_in_app": "Designação legível da obra ou estudo — listas e exportações mestres.",
        "workflow_context": "Criação do projecto; contexto comum a fascículos.",
        "when_to_use": "Sempre ao criar; único no seu workspace.",
        "related_concepts": ["project"],
        "related_screen": "project"},
    "project.intervention": {
        "purpose_in_app": "Tipo de contexto (ex. brownfield/greenfield) para enquadrar premissas e risco.",
        "workflow_context": "Metadados do projecto.",
        "when_to_use": "Ao criar; influencia documentação esperada.",
        "related_concepts": ["project"],
        "related_screen": "project"},
    "project.active": {
        "purpose_in_app": "Selecciona qual projecto recebe estrutura, blocos e exportações.",
        "workflow_context": "Após criar vários projectos.",
        "when_to_use": "Sempre que muda de obra no mesmo workspace.",
        "related_concepts": ["project", "workspace"],
        "related_screen": "project"},
    "document.tree": {
        "purpose_in_app": "Visualiza fascículos e blocos — índice do caderno, não o texto.",
        "workflow_context": "Estrutura documental.",
        "when_to_use": "Ao organizar F04, blocos e ordem.",
        "related_concepts": ["fascicle", "block"],
        "related_screen": "project-structure"},
    "document.assoc_item": {
        "purpose_in_app": "Liga conhecimento da biblioteca ou projecto a um nó da árvore.",
        "workflow_context": "Associações na estrutura.",
        "when_to_use": "Quando um capítulo referencia unidades aprovadas.",
        "related_concepts": ["knowledge_item", "block"],
        "related_screen": "project-structure"},
    "document.assoc_role": {
        "purpose_in_app": "Papel da ligação (fundamentação, requisito citado, etc.).",
        "workflow_context": "Ao associar conhecimento a nó.",
        "when_to_use": "Para a exportação distinguir suporte de obrigatoriedade.",
        "related_concepts": ["knowledge_item"],
        "related_screen": "project-structure"},
    "document.assoc_instruction": {
        "purpose_in_app": "Instrução específica de como usar a unidade ligada neste nó.",
        "workflow_context": "Associação documental.",
        "when_to_use": "Quando a mesma unidade serve papéis diferentes em blocos.",
        "related_concepts": ["knowledge_item"],
        "related_screen": "project-structure"},
    "document.node_type": {
        "purpose_in_app": "Distingue fascículo, bloco, secção na árvore.",
        "workflow_context": "Criação de nós.",
        "when_to_use": "Ao expandir estrutura; blocos recebem pontos.",
        "related_concepts": ["fascicle", "block"],
        "related_screen": "project-structure"},
    "document.title": {
        "purpose_in_app": "Título apresentado do nó na árvore e exportações.",
        "workflow_context": "Estrutura documental.",
        "when_to_use": "Ao criar fascículo ou bloco.",
        "related_concepts": ["fascicle", "block"],
        "related_screen": "project-structure"},
    "document.parent": {
        "purpose_in_app": "Posiciona o nó na hierarquia projecto → fascículo → bloco.",
        "workflow_context": "Criação/edição de nós.",
        "when_to_use": "Ao aninhar ou mover na árvore.",
        "related_concepts": ["fascicle", "block"],
        "related_screen": "project-structure"},
    "technical.instance_name": {
        "purpose_in_app": "Nome da instância técnica (sistema, equipamento, função).",
        "workflow_context": "Árvore técnica do projecto.",
        "when_to_use": "Modelar instâncias exportáveis.",
        "related_concepts": ["project"],
        "related_screen": "project-technical"},
    "technical.kind": {
        "purpose_in_app": "Tipo da instância (sistema, equipamento, função).",
        "workflow_context": "Árvore técnica.",
        "when_to_use": "Ao criar nó técnico.",
        "related_concepts": ["project"],
        "related_screen": "project-technical"},
    "technical.parent": {
        "purpose_in_app": "Hierarquia técnica pai/filho.",
        "workflow_context": "Árvore técnica.",
        "when_to_use": "Ao aninhar sistemas e funções.",
        "related_concepts": ["project"],
        "related_screen": "project-technical"},
    "export.baseline": {
        "purpose_in_app": "Congela revisões aprovadas antes de export mestre ou fascículo — reprodutibilidade.",
        "workflow_context": "Ecrã Exportar; distinto do pacote exchange por bloco.",
        "when_to_use": "Quando o conjunto está fixo para discussão/redacção externa.",
        "related_concepts": ["baseline", "project"],
        "related_screen": "export"},
    "export.fascicle": {
        "purpose_in_app": "Limita exportação a um fascículo (subconjunto do projecto).",
        "workflow_context": "Exportar fascículo após baseline.",
        "when_to_use": "Trabalho incremental por domínio (F04, F05, …).",
        "related_concepts": ["fascicle", "baseline"],
        "related_screen": "export"},
    "export.zip": {
        "purpose_in_app": "Arquiva JSON, Markdown derivado e validation.json em ZIP — arquivo, não reimportação.",
        "workflow_context": "Opção no export mestre/fascículo.",
        "when_to_use": "Entrega a terceiros ou arquivo; JSON continua canónico.",
        "related_concepts": ["baseline"],
        "related_screen": "export"},
    "import.fascicle": {
        "purpose_in_app": "Contexto do roundtrip: qual fascículo o JSON devolvido pretende actualizar.",
        "workflow_context": "Reimportação após trabalho LLM.",
        "when_to_use": "Validar origem do ficheiro.",
        "related_concepts": ["reimport"],
        "related_screen": "import"},
    "import.omission": {
        "purpose_in_app": "Lembra que omissão no JSON não apaga dados no GET.",
        "workflow_context": "Antes de aprovar merge.",
        "when_to_use": "Sempre na reimportação.",
        "related_concepts": ["reimport"],
        "related_screen": "import"},
    "backup.critical": {
        "purpose_in_app": "Operações de backup/restauro da base SQLite do workspace.",
        "workflow_context": "Ecrã Backups.",
        "when_to_use": "Antes de consolidação grande ou migração.",
        "related_concepts": ["workspace"],
        "related_screen": "backups"},
    "knowledge.draft": {
        "purpose_in_app": "Distingue elaboração temporária de revisão concluída — exportações fiáveis usam conhecimento aprovado.",
        "workflow_context": "Ciclo de vida da unidade na biblioteca ou projecto.",
        "when_to_use": "Enquanto edita; concluir revisão quando estiver pronto para exportar.",
        "related_concepts": ["knowledge_item"],
        "related_screen": "library"},
}


def _force_entry(entry: dict, patch: dict) -> None:
    for k, v in patch.items():
        if v is not None:
            entry[k] = v


def _strip_generic_fields(data: dict) -> None:
    """Substitui purpose_in_app genéricos restantes por texto mínimo alinhado ao método."""
    for key, entry in data["fields"].items():
        p = entry.get("purpose_in_app") or ""
        if GENERIC_PREFIX.match(p) or not p.strip():
            family = key.split(".", 1)[0]
            entry["purpose_in_app"] = (
                f"Campo «{entry.get('label', key)}» no fluxo GET ({family}): "
                "regista dado estruturado para SQLite e exportação JSON, não redação final."
            )
        if not entry.get("workflow_context"):
            entry["workflow_context"] = (
                "No método GET: estrutura → validação → exportação → LLM externa → revisão."
            )
        entry.setdefault("when_to_use", f"Quando edita «{entry.get('label', key)}».")
        entry.setdefault("what_happens_next", "Valor gravado no workspace; pode entrar em validações e exportações.")


def _enhance_block_template(data: dict) -> None:
    tpl = data["fields"].get("block.template")
    if not tpl or not TEMPLATES.exists():
        return
    templates = json.loads(TEMPLATES.read_text(encoding="utf-8")).get("templates", [])
    names = ", ".join(t["name"] for t in templates[:6])
    extra = f" Modelos no catálogo: {names}, etc. Criam prompts vazios, não decisões."
    tpl["what_happens_next"] = (tpl.get("what_happens_next") or "") + extra
    tpl.setdefault("related_concepts", ["development_point_template", "development_point"])


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    data["catalog_version"] = "1.3.0"
    data["method"] = METHOD
    data["concepts"] = CONCEPTS_V13
    data["workflows"] = WORKFLOWS

    for sid, extra in SCREEN_EXTRA.items():
        if sid in data.get("screens", {}):
            data["screens"][sid].update(extra)

    for key, patch in DEV_POINT_FORCE.items():
        if key not in data["fields"]:
            data["fields"][key] = {"label": key.split(".", 1)[1], "short_help": "", "definition": ""}
        _force_entry(data["fields"][key], patch)

    for key, patch in FAMILY_FORCE.items():
        if key in data["fields"]:
            _force_entry(data["fields"][key], patch)

    _strip_generic_fields(data)
    _enhance_block_template(data)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", CATALOG, "v", data["catalog_version"], "fields", len(data["fields"]))


if __name__ == "__main__":
    main()