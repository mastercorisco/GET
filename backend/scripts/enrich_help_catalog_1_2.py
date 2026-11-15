"""Enriquece get_help_catalog.pt-PT.json para v1.2.0 (ajuda orientada ao utilizador GET)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalogs" / "get_help_catalog.pt-PT.json"

CONCEPTS_V12 = {
    "block": {
        "label": "Bloco",
        "summary": "Unidade documental (ex.: capítulo F04_B03) que vai para o caderno.",
        "role_in_get": "No GET, o bloco é o recipiente onde prepara objectivo, âmbito e pontos de desenvolvimento antes de exportar um pacote JSON para a LLM. Não é o texto final do caderno — é a instrução estruturada.",
        "not_this": "Não é um ficheiro Word, nem a resposta da LLM; é a unidade de trabalho dentro da árvore documental.",
    },
    "development_point": {
        "label": "Ponto de desenvolvimento",
        "summary": "Um assunto técnico que a LLM deve desenvolver, por ordem.",
        "role_in_get": "Cada ponto traduz uma ideia técnica em instruções verificáveis (ideia, obrigatórios, limites, critérios). A app valida e exporta; a LLM redige fora do GET.",
        "not_this": "Não é um parágrafo do caderno nem um requisito solto no Excel — é o contrato de desenvolvimento para um tema.",
    },
    "premise": {
        "label": "Premissa",
        "summary": "Condição assumida verdadeira para enquadrar o desenvolvimento.",
        "role_in_get": "Premissas entram no pacote exchange para a LLM não inventar contexto. Podem existir ao nível do bloco, fascículo, projecto ou ponto.",
        "not_this": "Não é um requisito ao adjudicatário; é «consideramos que…» até decisão contrária.",
    },
    "knowledge_item": {
        "label": "Unidade de conhecimento",
        "summary": "Conteúdo técnico reutilizável (biblioteca ou projecto).",
        "role_in_get": "A biblioteca EDA alimenta vários projectos. No projecto, o conhecimento pode ser específico do caderno. Exportações referenciam unidades aprovadas.",
        "not_this": "Não é texto livre na exportação final; tem identidade, revisão e ciclo de vida na base de dados.",
    },
    "reference": {
        "label": "Referência",
        "summary": "Fonte normativa, documental ou técnica citável.",
        "role_in_get": "Associa-se a conhecimento, premissas ou fichas normativas. Aparece nas exportações como suporte, não como texto integral.",
        "not_this": "Não substitui o conteúdo técnico escrito pelo utilizador ou pela LLM.",
    },
    "open_question": {
        "label": "Questão pendente",
        "summary": "Lacuna que ninguém deve fechar sem decisão humana.",
        "role_in_get": "Regista incertezas para a LLM não assumir respostas. Pode surgir em pontos ou em conhecimento.",
        "not_this": "Não é um requisito nem uma premissa confirmada.",
    },
    "workspace": {
        "label": "Workspace",
        "summary": "Pasta local com a base SQLite e exportações do GET.",
        "role_in_get": "Separa dados do código da aplicação. Um workspace = um conjunto de projectos e backups na sua máquina.",
        "not_this": "Não é o repositório Git nem a pasta do executável GET.",
    },
    "baseline": {
        "label": "Baseline",
        "summary": "Instantâneo aprovado antes de exportações mestres.",
        "role_in_get": "Fixa revisões para exportações determinísticas. Sem baseline publicada, algumas exportações avisam que o estado não está congelado.",
        "not_this": "Não é um backup de ficheiros; é um marco de versão dentro do SQLite.",
    },
    "exchange_package": {
        "label": "Pacote exchange",
        "summary": "JSON por bloco para trabalho com LLM externa.",
        "role_in_get": "Sai da Preparação do bloco; contém objectivo, pontos, premissas e listas. A LLM devolve JSON noutro fluxo (reimportação), não neste pacote.",
        "not_this": "Não é o export mestre do projecto inteiro nem um .docx.",
    },
}

# Chaves com texto editorial completo (fase 1 + pontos + export/import)
OVERRIDES: dict[str, dict] = {}

def _o(
    key: str,
    *,
    purpose: str,
    workflow: str,
    when: str,
    next_: str = "",
    confusions: list[str] | None = None,
    concepts: list[str] | None = None,
    screen: str | None = None,
    short: str | None = None,
):
    OVERRIDES[key] = {
        "purpose_in_app": purpose,
        "workflow_context": workflow,
        "when_to_use": when,
        "what_happens_next": next_,
        "common_confusions": confusions or [],
        "related_concepts": concepts or [],
        "related_screen": screen,
    }
    if short:
        OVERRIDES[key]["short_help"] = short


_o(
    "workspace.root_path",
    purpose="Indica ao GET onde guardar a base de dados, backups e ficheiros exportados — a «pasta de trabalho» do caderno na sua máquina.",
    workflow="Primeiro passo ao usar o GET: sem workspace não há biblioteca, projectos nem exportações.",
    when="Antes de criar ou abrir qualquer dado. Use uma pasta dedicada (ex.: D:\\GET-dados\\obra-X).",
    next_="Ao criar ou abrir, o GET regista o caminho em configuração local e mostra o menu completo da aplicação.",
    confusions=["Confundir com a pasta do código-fonte GET.", "Usar uma pasta partilhada em rede sem controlo de concorrência (MVP é um utilizador local)."],
    concepts=["workspace"],
    screen="workspace",
    short="Pasta local onde o GET guarda o SQLite e os exports.",
)

_o(
    "workspace.user_name",
    purpose="Nome gravado nas operações para saber quem alterou conteúdo (proveniência). O GET não tem login.",
    workflow="Ao criar o workspace; pode ser o mesmo em todas as sessões.",
    when="Sempre que cria workspace novo; ao abrir pode manter o anterior.",
    next_="Aparece em metadados de revisão e exportação; não bloqueia funcionalidades.",
    confusions=["Pensar que é palavra-passe ou conta de utilizador."],
    concepts=["workspace"],
    screen="workspace",
)

_o(
    "workspace.help_level",
    purpose="Controla quanta ajuda vê na interface: ícones (i), popups explicativos ou também microtexto sob campos.",
    workflow="Pode ajustar no ecrã Configurações quando o workspace está aberto.",
    when="Se os popups forem suficientes use Normal; se quiser pistas sempre visíveis use Detailed.",
    next_="Gravado nas preferências do workspace; afecta todos os ecrãs com ícone (i).",
    concepts=["workspace"],
    screen="settings",
    short="Normal: ajuda em popup ao carregar em (i).",
)

_o(
    "knowledge.title",
    purpose="Identifica a unidade na lista e nas exportações — o «nome» do conhecimento na biblioteca.",
    workflow="Biblioteca EDA, antes de associar conhecimento a nós da árvore ou a pontos.",
    when="Ao criar qualquer entrada na biblioteca; título curto e único no seu contexto.",
    next_="Fica na SQLite; pesquisa FTS usa o título.",
    concepts=["knowledge_item"],
    screen="library",
)

_o(
    "knowledge.content",
    purpose="Corpo técnico do conhecimento (texto sanitizado). É o que exporta para discussão com a LLM.",
    workflow="Biblioteca ou conhecimento do projecto; depois pode associar a estrutura documental.",
    when="Sempre que regista facto, requisito, decisão, etc.",
    next_="Revisões futuras criam nova versão; conteúdo aprovado não é apagado silenciosamente.",
    confusions=["Colar aqui o capítulo inteiro do Word em vez de unidades atómicas."],
    concepts=["knowledge_item"],
    screen="library",
)

_o(
    "knowledge.origin_context",
    purpose="Explica de onde veio a informação (reunião, documento, decisão) para quem lê exportações meses depois.",
    workflow="Obrigatório na captura mínima; acompanha a unidade em exportações JSON.",
    when="No momento de criar ou rever a unidade.",
    next_="Visível em exportações; não é texto que a LLM devolve na reimportação para alterar.",
    concepts=["knowledge_item"],
    screen="library",
)

_o(
    "export.profile",
    purpose="Escolhe se o JSON destina-se a discussão (mais contexto) ou redação (mais focado em texto).",
    workflow="Ecrã Exportar, após baseline; não confundir com o pacote exchange por bloco.",
    when="Ao exportar fascículo ou mestre para a LLM externa.",
    next_="Gera ficheiros na pasta exports do workspace; perfis têm campos diferentes.",
    confusions=["Confundir com exportação do bloco (preparação) que usa get_exchange_package."],
    concepts=["baseline", "exchange_package"],
    screen="export",
)

_o(
    "import.file",
    purpose="Carrega JSON devolvido pela LLM para análise de diferenças — não consolida automaticamente.",
    workflow="Depois de trabalhar o JSON exportado fora do GET; reimportação → propostas → aprovação humana.",
    when="Quando recebe ficheiro roundtrip estruturado da LLM.",
    next_="Entra em staging; merge three-way antes de aprovar alterações.",
    confusions=["Achar que omissão no JSON apaga dados no GET.", "Importar Word ou Markdown (não suportado como reimportação)."],
    concepts=["baseline"],
    screen="import",
)

_o(
    "block.objective",
    purpose="Diz à LLM o que este bloco do caderno deve produzir como mensagem global (nível capítulo).",
    workflow="Preparação do bloco, antes dos pontos e da exportação exchange.",
    when="Ao abrir um bloco na estrutura; revise quando o âmbito do capítulo mudar.",
    next_="Gravado no SQLite; incluído no pacote JSON para a LLM.",
    concepts=["block", "exchange_package"],
    screen="block-editor",
)

_o(
    "block.scope",
    purpose="Limita o que pertence a este bloco e o que fica fora, para a LLM não alargar o assunto.",
    workflow="Junto com objectivo; lê-se antes dos pontos na exportação.",
    when="Sempre que o bloco ganha fronteiras novas (sistemas, locais, fases).",
    next_="Exportado no cabeçalho do bloco no pacote exchange.",
    concepts=["block"],
    screen="block-editor",
)

_o(
    "block.target_output",
    purpose="Descreve em JSON o formato esperado do resultado (ex.: secção de especificação, tabela). Orienta a LLM sem ser texto final.",
    workflow="Opcional mas útil antes de exportar; validado como JSON.",
    when="Quando o adjudicatário ou o modelo exige estrutura concreta de entrega.",
    next_="Incluído no JSON do bloco na exportação.",
    concepts=["block", "exchange_package"],
    screen="block-editor",
)

_o(
    "premise.statement",
    purpose="Regista uma condição assumida verdadeira para este bloco (ou ponto), não um requisito.",
    workflow="Preparação do bloco → premissas; aparecem no pacote para a LLM.",
    when="Há pressupostos de projeto, normas ou decisões que devem ser explícitos.",
    next_="Gravado em SQLite; visível na exportação exchange.",
    confusions=["Escrever aqui um requisito «deve» em vez de «assume-se que»."],
    concepts=["premise", "block"],
    screen="block-editor",
)

_o(
    "development_point.overview",
    purpose="Visão geral do cartão de ponto: resume o que é um ponto dentro do GET.",
    workflow="Ao expandir um ponto na lista do bloco.",
    when="Quando cria o primeiro ponto ou precisa de rever a estrutura.",
    next_="O detalhe guarda-se ao expandir o cartão.",
    concepts=["development_point", "block"],
    screen="block-editor",
)

# Campos HTML adicionais (fase 1)
_o(
    "knowledge.search",
    purpose="Pesquisa texto nas unidades da biblioteca (FTS) sem substituir estrutura ou revisões.",
    workflow="Biblioteca EDA, antes de abrir ou editar uma unidade.",
    when="Quando procura conhecimento existente para reutilizar ou rever.",
    next_="Mostra lista filtrada; não altera dados até abrir uma unidade.",
    concepts=["knowledge_item"],
    screen="library",
)
_o(
    "knowledge.profile_type",
    purpose="Classifica a unidade (ex.: fact, requirement) para exportações e validação.",
    workflow="Formulário da biblioteca ou detalhe de conhecimento.",
    when="Ao criar ou rever metadados da unidade.",
    next_="Influencia perfis de exportação discussion/redaction.",
    concepts=["knowledge_item"],
    screen="library",
)
_o(
    "knowledge.profile_data",
    purpose="Atributos extra do perfil em JSON; estende o tipo sem mudar o corpo principal.",
    workflow="Biblioteca, quando o tipo exige campos adicionais.",
    when="Quando o profile_type pede estrutura complementar documentada.",
    next_="Validado como JSON; exportado com a unidade.",
    concepts=["knowledge_item"],
    screen="library",
)
_o(
    "library.ref_title",
    purpose="Nome curto da referência na biblioteca global (normas, manuais, decisões).",
    workflow="Biblioteca → referências.",
    when="Ao registar uma fonte citável reutilizável em vários projectos.",
    next_="Pode associar-se a conhecimento, premissas ou pontos por ID.",
    concepts=["reference"],
    screen="library",
)
_o(
    "library.ref_citation",
    purpose="Texto de citação (edição, secção, data) para exportações e rastreio.",
    workflow="Junto com título da referência na biblioteca.",
    when="Sempre que a referência deve ser localizável fora do GET.",
    next_="Aparece nas ligações exportadas, não como PDF anexo.",
    concepts=["reference"],
    screen="library",
)
_o(
    "library.term_preferred",
    purpose="Termo canónico do glossário EDA para consistência entre projectos.",
    workflow="Biblioteca → termos.",
    when="Ao definir vocabulário comum (siglas, conceitos).",
    next_="Sinónimos apontam para este termo nas exportações.",
    concepts=["knowledge_item"],
    screen="library",
)
_o(
    "library.term_definition",
    purpose="Definição acordada do termo preferencial.",
    workflow="Glossário da biblioteca.",
    when="Quando o termo precisa de enquadramento técnico explícito.",
    next_="Reutilizado em validações e texto exportado por referência.",
    concepts=["knowledge_item"],
    screen="library",
)
_o(
    "library.term_synonyms",
    purpose="Variantes aceites que mapeiam para o termo preferencial.",
    workflow="Glossário, após o termo preferencial.",
    when="Há nomes alternativos usados em documentos legados.",
    next_="Ajuda pesquisa e consistência; não cria entradas duplicadas.",
    concepts=["knowledge_item"],
    screen="library",
)
_o(
    "workbook.validate_file",
    purpose="Valida estrutura do modelo Excel de requisitos sem importar para o SQLite.",
    workflow="Ecrã modelo workbook, antes de ligações ao projecto.",
    when="Ao receber ou actualizar a folha de requisitos.",
    next_="Relatório de erros/avisos; não altera conhecimento automaticamente.",
    confusions=["Confundir com reimportação JSON da LLM."],
    screen="workbook",
)
_o(
    "block.template",
    purpose="Copia estrutura de outro ponto ao criar um novo, para acelerar preparação.",
    workflow="Preparação do bloco → adicionar ponto.",
    when="Pontos repetem o mesmo esqueleto (orientações, critérios).",
    next_="Novo ponto herda listas; títulos e ideia central deve rever-se.",
    concepts=["block", "development_point"],
    screen="block-editor",
)
_o(
    "block.points_overview",
    purpose="Secção onde ordena e edita pontos — o núcleo do pacote exchange para a LLM.",
    workflow="Depois de objectivo/âmbito; antes de validar e exportar.",
    when="Sempre que o bloco precisa de conteúdo desenvolvido por pontos.",
    next_="Cada ponto guardado entra na validação e no JSON do bloco.",
    concepts=["development_point", "exchange_package"],
    screen="block-editor",
)
_o(
    "block.include_draft",
    purpose="Inclui pontos ainda em rascunho na exportação exchange (com aviso).",
    workflow="Imediatamente antes de exportar o pacote do bloco.",
    when="Quer enviar trabalho em curso à LLM com responsabilidade explícita.",
    next_="JSON marca estado draft; validação pode listar problemas.",
    concepts=["block", "exchange_package"],
    screen="block-editor",
)
_o(
    "premise.importance",
    purpose="Prioriza premissas: críticas devem ser lidas antes de pontos dependentes.",
    workflow="Formulário de premissa no bloco.",
    when="Várias premissas competem por atenção na exportação.",
    next_="Ordenação e destaque na lista exportada.",
    concepts=["premise"],
    screen="block-editor",
)
_o(
    "premise.source_type",
    purpose="Indica se a premissa vem de decisão, norma, reunião, etc.",
    workflow="Ao criar premissa no bloco.",
    when="Para rastreio e confiança na reimportação futura.",
    next_="Metadado no SQLite e no JSON exportado.",
    concepts=["premise"],
    screen="block-editor",
)
_o(
    "premise.confidence",
    purpose="Grau de certeza da premissa — evita que a LLM trate hipóteses como factos.",
    workflow="Junto com o enunciado da premissa.",
    when="A condição não está totalmente confirmada.",
    next_="A LLM deve respeitar baixa confiança com questões ou ressalvas.",
    concepts=["premise", "open_question"],
    screen="block-editor",
)
_o(
    "settings.theme",
    purpose="Esquema claro/escuro só nesta máquina; não altera exportações.",
    workflow="Configurações com workspace aberto.",
    when="Conforto visual ou ambiente de trabalho.",
    next_="Gravado em ui-preferences local.",
    concepts=["workspace"],
    screen="settings",
)
_o(
    "settings.accent",
    purpose="Escolhe preset ou cor personalizada dos botões e realces.",
    workflow="Configurações → aparência.",
    when="Quer destacar acções principais com cor habitual da equipa.",
    next_="CSS variables actualizadas na hora.",
    screen="settings",
)
_o(
    "settings.accent_color",
    purpose="Cor hexadecimal exacta quando o preset não chega.",
    workflow="Configurações, modo personalizado de destaque.",
    when="Marca ou contraste específico.",
    next_="Validação de formato #RRGGBB.",
    screen="settings",
)
_o(
    "settings.font",
    purpose="Família tipográfica da UI local.",
    workflow="Configurações.",
    when="Legibilidade ou alinhamento com outros documentos.",
    next_="Não afecta tipografia do caderno exportado.",
    screen="settings",
)
_o(
    "settings.font_custom",
    purpose="font-family CSS quando escolhe tipo personalizado.",
    workflow="Configurações → tipo de letra personalizado.",
    when="A lista preset não inclui a fonte desejada.",
    next_="Aplicado a toda a interface GET nesta máquina.",
    screen="settings",
)
_o(
    "settings.density",
    purpose="Controlos compactos ou confortáveis — densidade global dos campos.",
    workflow="Configurações.",
    when="Monitor pequeno vs. leitura prolongada.",
    next_="Combina com rem de padding e altura de textarea.",
    screen="settings",
)
_o(
    "settings.control_font_size",
    purpose="Tamanho base em rem dos textos nos formulários.",
    workflow="Configurações, modo detalhado de densidade.",
    when="Ajuste fino além do preset de densidade.",
    next_="Afecta inputs e etiquetas via CSS variables.",
    screen="settings",
)
_o(
    "settings.control_padding_block",
    purpose="Espaço vertical dentro dos campos de entrada.",
    workflow="Configurações avançadas de aparência.",
    when="Campos parecem apertados ou demasiado altos.",
    next_="Preview reflecte valor antes de gravar.",
    screen="settings",
)
_o(
    "settings.control_padding_inline",
    purpose="Espaço horizontal dentro dos campos.",
    workflow="Configurações avançadas.",
    when="Texto encosta às bordas dos inputs.",
    next_="Gravado em ui-preferences.",
    screen="settings",
)
_o(
    "settings.textarea_min_height",
    purpose="Altura mínima de áreas multilinha (objectivos, conteúdo).",
    workflow="Configurações.",
    when="Escreve parágrafos longos na Preparação do bloco ou biblioteca.",
    next_="Aplica-se a textareas em todos os ecrãs.",
    screen="settings",
)
_o(
    "settings.ui_scale",
    purpose="Escala percentual de toda a interface (acessibilidade).",
    workflow="Configurações.",
    when="Precisa de zoom global sem mudar resolução do OS.",
    next_="Pode combinar com largura máxima de conteúdo.",
    screen="settings",
)
_o(
    "settings.content_width",
    purpose="Limita largura da coluna principal (lectura confortável).",
    workflow="Configurações.",
    when="Ecrã muito largo dispersa o foco.",
    next_="Opção personalizada usa pixels máximos.",
    screen="settings",
)
_o(
    "settings.content_max_px",
    purpose="Largura máxima em pixels do conteúdo central.",
    workflow="Quando content_width é personalizado.",
    when="Quer valor exacto (ex.: 1200px).",
    next_="Preview e ecrãs principais seguem o limite.",
    screen="settings",
)

DEV_POINT_PURPOSE = {
    "title": (
        "Dá nome ao assunto no índice do bloco e no JSON para a LLM.",
        "Lista de pontos na Preparação do bloco.",
        "Ao criar ou renomear um ponto.",
    ),
    "core_idea": (
        "Afirmação técnica que a LLM não pode contradizer — âncora do ponto.",
        "Cartão expandido do ponto, antes de listas e critérios.",
        "Sempre; é o campo mais importante do ponto.",
    ),
    "intended_outcome": (
        "O que o leitor deve concluir após o texto desenvolvido.",
        "Depois da ideia central.",
        "Quando o resultado esperado não é óbvio só pela ideia.",
    ),
    "development_guidance": (
        "Instruções de forma e enfoque, não requisitos escondidos.",
        "Secção Orientações do cartão.",
        "Quando a LLM precisa de estrutura ou ênfases.",
    ),
    "premises": (
        "Condições assumidas para este ponto concreto.",
        "Secção Premissas do cartão.",
        "Quando o ponto depende de pressupostos.",
    ),
    "must_include": (
        "Matéria que tem de aparecer no desenvolvimento.",
        "Secção Obrigatórios.",
        "Quando há elementos não negociáveis.",
    ),
    "limits_and_exclusions": (
        "O que o desenvolvimento não deve cobrir.",
        "Secção Limites.",
        "Para evitar scope creep na resposta da LLM.",
    ),
    "questions_to_answer": (
        "Liga conhecimento e referências da biblioteca a este ponto.",
        "Secção Conhecimento e referências.",
        "Quando o ponto apoia-se em unidades já aprovadas.",
    ),
    "open_questions": (
        "Lacunas que a LLM não deve fechar sozinha.",
        "Secção Questões.",
        "Quando há decisões pendentes.",
    ),
    "acceptance_criteria": (
        "Como verificar se o texto desenvolvido cumpre o ponto.",
        "Secção Critérios.",
        "Antes de considerar o ponto pronto para exportação.",
    ),
    "llm_freedom": (
        "Grau de liberdade textual da LLM dentro dos limites definidos.",
        "Secção Estado e LLM.",
        "Quando quer redação mais rígida ou mais explanatória.",
    ),
    "status": (
        "Ciclo de vida do ponto (rascunho, pronto, etc.).",
        "Secção Estado e LLM.",
        "Antes de exportar; rascunhos podem ficar de fora.",
    ),
}


def apply_development_points(data: dict) -> None:
    for key, (purpose, workflow, when) in DEV_POINT_PURPOSE.items():
        fkey = "development_point." + key
        if fkey not in data["fields"]:
            continue
        entry = data["fields"][fkey]
        entry.setdefault("purpose_in_app", purpose)
        entry.setdefault(
            "workflow_context",
            f"{workflow} No fluxo: estrutura → bloco → validação → pacote exchange.",
        )
        entry.setdefault("when_to_use", when)
        entry.setdefault(
            "what_happens_next",
            "Guardado com o ponto no SQLite; incluído na exportação JSON do bloco.",
        )
        entry.setdefault("related_concepts", ["development_point", "exchange_package"])
        entry.setdefault("related_screen", "block-editor")
        entry.setdefault(
            "common_confusions",
            ["Meter requisitos completos só no título.", "Confundir orientações com obrigatórios."],
        )

GENERIC_WORKFLOW = {
    "settings": ("Configurações", "ecrã Configurações", "settings", []),
    "library": ("Biblioteca EDA", "menu Biblioteca", "library", ["knowledge_item", "reference"]),
    "workbook": ("Modelo Excel", "ecrã Modelo Excel", "workbook", []),
    "project": ("Projecto", "ecrã Projecto", "project", ["knowledge_item"]),
    "document": ("Estrutura documental", "árvore fascículo/bloco", "project-structure", ["block"]),
    "technical": ("Árvore técnica", "ecrã Árvore técnica", "project-technical", []),
    "backup": ("Backups", "ecrã Backups", "backups", ["workspace"]),
    "export": ("Exportação", "ecrã Exportar para LLM", "export", ["baseline"]),
    "import": ("Reimportação", "ecrã Reimportar", "import", ["baseline"]),
    "premise": ("Premissa", "Preparação do bloco", "block-editor", ["premise"]),
    "block": ("Bloco", "Preparação do bloco", "block-editor", ["block"]),
    "development_point": ("Ponto de desenvolvimento", "cartão expandido do ponto", "block-editor", ["development_point"]),
}


def apply_generic(key: str, entry: dict) -> None:
    prefix = key.split(".", 1)[0]
    if key in OVERRIDES:
        return
    tpl = GENERIC_WORKFLOW.get(prefix)
    if not tpl:
        return
    label = entry.get("label") or key
    area, place, screen, concepts = tpl
    entry.setdefault(
        "purpose_in_app",
        f"No GET, este campo «{label}» pertence a {area}: ajuda a preparar dados que ficam na base SQLite e podem sair em exportações JSON.",
    )
    entry.setdefault(
        "workflow_context",
        f"Preenchido no {place}, no fluxo de construção do caderno antes de exportar para a LLM externa.",
    )
    entry.setdefault(
        "when_to_use",
        f"Quando trabalha em {area} e precisa de registar ou ajustar «{label}».",
    )
    entry.setdefault(
        "what_happens_next",
        "Ao guardar (ou ao sair do campo, nos cartões de ponto), o valor fica no workspace e entra em validações e exportações conforme o tipo de dado.",
    )
    entry.setdefault("related_concepts", concepts)
    entry.setdefault("related_screen", screen)
    entry.setdefault("common_confusions", [f"Tratar este campo como se fosse redação final do Word, em vez de dado estruturado do GET."])


SCREEN_V12 = {
    "workspace": {
        "audience_note": "Se chegou agora ao GET: comece aqui — nada mais funciona até existir uma pasta de dados (workspace).",
        "purpose_steps": [
            "Indicar o caminho — para o GET saber onde criar a base SQLite e as pastas exports/imports.",
            "Criar ou abrir — para carregar ou inicializar o ficheiro get.db.",
            "Opcional: ajustar ajuda em Configurações — para ver mais ou menos explicações na interface.",
        ],
    },
    "library": {
        "audience_note": "A biblioteca é conhecimento reutilizável; ainda não está ligada a um capítulo específico do caderno.",
        "purpose_steps": [
            "Criar unidades com título, conteúdo e contexto — para poder reutilizar e pesquisar depois.",
            "Rever estados quando o conhecimento amadurecer — para exportações fiáveis.",
            "Adicionar referências e termos — para consistência em todos os projectos.",
        ],
    },
    "project-structure": {
        "audience_note": "A árvore não é o texto do caderno: é o índice de fascículos, blocos e secções.",
        "purpose_steps": [
            "Criar fascículos e blocos — para espelhar a estrutura do documento final.",
            "Seleccionar um bloco — para abrir a Preparação do bloco (pontos para a LLM).",
            "Associar conhecimento a nós — para exportar ligações, não o texto integral solto.",
        ],
    },
    "block-editor": {
        "audience_note": "Aqui define instruções para a LLM; o GET não escreve o caderno por si.",
        "purpose_steps": [
            "Objectivo e âmbito — enquadram o capítulo no pacote JSON.",
            "Premissas e pontos ordenados — contrato do que a LLM pode e não pode inventar.",
            "Validação e exportação exchange — gera o ficheiro que envia à LLM externa.",
        ],
    },
    "export": {
        "audience_note": "Exportar mestre/fascículo é diferente do pacote por bloco na Preparação.",
        "purpose_steps": [
            "Publicar baseline quando o conjunto estiver fixo — para exportações reproduzíveis.",
            "Escolher perfil discussion/redaction — para a LLM receber o nível certo de contexto.",
            "Gravar JSON na pasta exports — para trabalho offline com Copilot/Claude/etc.",
        ],
    },
    "import": {
        "audience_note": "Reimportação é revisão humana: nada entra na base sem aprovação.",
        "purpose_steps": [
            "Carregar JSON devolvido — entra em staging, não substitui tudo.",
            "Analisar merge — compara base exportada, estado actual e ficheiro devolvido.",
            "Decidir proposta a proposta — consolida só o que aprovar.",
        ],
    },
    "settings": {
        "audience_note": "Aparência é só desta máquina; não viaja no JSON do caderno.",
        "purpose_steps": [
            "Ajustar tema e densidade — conforto visual local.",
            "Nível de ajuda — mais popups ou também texto sob campos.",
        ],
    },
}


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    data["catalog_version"] = "1.2.0"
    data["_schema_note"] = (
        "Campos de campo (fields.*): purpose_in_app, workflow_context, when_to_use, "
        "what_happens_next, related_concepts, related_screen, common_confusions."
    )
    data["concepts"] = CONCEPTS_V12

    for screen_id, extra in SCREEN_V12.items():
        if screen_id in data.get("screens", {}):
            data["screens"][screen_id].update(extra)

    for key, patch in OVERRIDES.items():
        if key not in data["fields"]:
            data["fields"][key] = {"label": key, "short_help": "", "definition": ""}
        entry = data["fields"][key]
        entry.update({k: v for k, v in patch.items() if v is not None and v != ""})

    apply_development_points(data)

    for key, entry in data["fields"].items():
        apply_generic(key, entry)

    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Wrote", CATALOG, "version", data["catalog_version"], "fields", len(data["fields"]))


if __name__ == "__main__":
    main()