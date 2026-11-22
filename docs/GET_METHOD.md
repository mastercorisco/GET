# Método GET para Estruturação de Conhecimento Técnico

## 1. Finalidade deste documento

Este documento descreve o método funcional da aplicação **GET — Gerador de Especificações Técnicas** e explica o papel de cada uma das suas partes.

O GET não é um gerador autónomo de texto e não contém inteligência artificial integrada. É uma aplicação local para organizar conhecimento técnico, decisões, premissas e assuntos a desenvolver antes de estes serem entregues a uma LLM externa, como o Microsoft Copilot ou o Claude.

A responsabilidade técnica permanece sempre no utilizador. A aplicação ajuda a estruturar, validar, reutilizar e exportar os inputs, mas não decide o conteúdo do caderno de encargos.

---

## 2. Princípio fundamental

O método separa claramente três atividades:

1. **Estruturar conhecimento**, realizado no GET.
2. **Desenvolver texto**, realizado por uma LLM externa.
3. **Validar tecnicamente o resultado**, realizado pelo utilizador.

Fluxo de trabalho:

```text
Utilizador de engenharia
        ↓
Aplicação GET
- organiza estrutura documental
- regista conhecimento
- define pontos a desenvolver
- controla premissas e limites
- identifica lacunas
        ↓
Exportação JSON estruturada
        ↓
LLM externa
- desenvolve cada ponto
- respeita a ordem e as premissas
- não inventa requisitos
- separa sugestões não aprovadas
        ↓
Revisão técnica humana
        ↓
Eventual reimportação controlada
```

O GET controla o **input autoritativo**. A LLM atua como meio de desenvolvimento e redação, não como autoridade técnica.

---

## 3. Organização geral do programa

```text
Biblioteca de conhecimento
└── KnowledgeItem

Projeto
└── Fascículo
    └── Bloco
        ├── Objetivo e âmbito
        ├── Premissas do bloco
        ├── Pontos de desenvolvimento
        │   ├── Ideia central
        │   ├── Orientações
        │   ├── Premissas
        │   ├── Elementos obrigatórios
        │   ├── Limites e exclusões
        │   ├── Questões
        │   └── Critérios de aceitação
        └── Ligações a conhecimento e referências
```

Existem duas estruturas complementares: **estrutura documental** (projeto, fascículos, blocos, pontos) e **estrutura de conhecimento** (unidades reutilizáveis e referências).

---

## 4. Projeto

O `Project` representa uma empreitada, instalação ou especificação concreta. Estabelece contexto comum: premissas transversais, fascículos e conhecimento específico. Exemplos de premissas de projeto: exploração em curso, migração faseada, neutralidade tecnológica, documentação em português de Portugal.

---

## 5. Fascículo

O `Fascicle` é um grande domínio do caderno (automação de campo, cibersegurança, ensaios, etc.). O identificador interno não depende da posição; a ordem pode mudar sem quebrar ligações.

---

## 6. Bloco

O `Block` é a unidade de preparação documental (ex.: `F04_B03 | Controladores locais e autonomia funcional`). Contém objectivo, âmbito, premissas, conhecimento, referências e pontos ordenados. Pode definir **target output** (tipo, idioma, tom, extensão, liberdade LLM). Não contém o texto final — contém inputs para produção externa.

---

## 7. Ponto de desenvolvimento

O `DevelopmentPoint` responde: *o que desenvolver, em que ordem e sob que condições?*

- **KnowledgeItem**: conhecimento que a organização possui e reutiliza.
- **DevelopmentPoint**: assunto a desenvolver num bloco concreto.

Campos principais: título, ideia central (afirmação técnica, não instrução de redação), resultado pretendido, orientações, perspectivas, questões a responder, premissas, obrigatórios, limites, exemplos, questões pendentes, critérios de aceitação.

---

## 8. Liberdade permitida à LLM (`llm_freedom`)

- **strict**: só desenvolve o fornecido; modo por defeito em cadernos.
- **bounded**: pode melhorar clareza; não altera premissas nem cria requisitos.
- **exploratory**: sugestões separadas; nunca aprovadas automaticamente.

---

## 9. Estados dos pontos

`draft`, `incomplete`, `ready`, `approved`, `obsolete`. `ready` exige conteúdo mínimo estrutural; `approved` valida inputs, não o texto da LLM. Exportação por defeito inclui `ready` e `approved`; `draft` só com opção explícita.

---

## 10. Premissas e herança

Níveis: projeto, fascículo, bloco, ponto. Na exportação reúnem-se sem duplicação física. Metadados: importância, confiança, origem.

---

## 11. Biblioteca de conhecimento

`KnowledgeItem` reutilizável (tipos: context, principle, requirement, decision, etc.). Ligações em projectos, não duplicações.

---

## 12. Sistema de ajuda contextual

- **Microajuda** (nível detailed): frase sob o campo.
- **Ícone (i)**: popup com narrativa GET → fluxo → definição → exemplos.
- **Painel de preparação**: encaminhamento, conceitos, validação, exportação.

Textos em `catalogs/get_help_catalog.pt-PT.json` (v1.3+). Níveis: `essential`, `normal` (recomendado), `detailed`. Sem geração de ajuda por LLM em runtime.

---

## 13. Modelos estruturais

Catálogo `development_point_templates.pt-PT.json`. Modelos criam prompts/campos vazios, não decisões.

---

## 14. Validação

Graus: informação, aviso, problema (bloqueio). Alertas concretos; sem pontuação abstracta 0–100.

---

## 15. Exportação JSON

**Por bloco (geração de texto):** contrato `get_llm_export.schema.json` (GET-LLM). JSON completo + Markdown derivado; secção `preparation` conserva o contrato editorial (pontos, premissas, lacunas). **Roundtrip:** `master` / `fascicle-roundtrip` para reimportação após baseline.

Áreas semânticas legadas do pacote exchange (agora dentro de `preparation` no GET-LLM):

- conteúdo autoritativo e pontos de desenvolvimento;
- contexto de apoio (conhecimento e referências);
- questões pendentes e lacunas;
- instruções de geração (regras em catálogo `llm_generation_rules.pt-PT.json`).

---

## 16. Reimportação controlada

Validação, comparação three-way, aprovação humana. Omissão no JSON não é eliminação. Conteúdo aprovado não substituído sem decisão.

---

## 17. Ecrãs principais

Projetos, estrutura, conhecimento, bloco de trabalho, importação/exportação.

---

## 18. Interface do bloco de trabalho

Cartões recolhíveis por ponto; secções: ideia, orientações, premissas, obrigatórios, limites, conhecimento, questões, critérios.

---

## 19. Arquitectura técnica (MVP actual)

- Python 3.12+
- FastAPI + aplicação web local (`127.0.0.1`)
- SQLite (fonte de verdade)
- SQLAlchemy 2, Alembic, Pydantic 2
- JSON Schema para contratos
- Shell estática (HTML/JS/CSS)
- pytest

Fora do MVP inicial: microserviços, PostgreSQL, autenticação multiutilizador, LLM integrada, geração Word.

---

## 20. Regras de governação

1. O utilizador é a autoridade técnica.
2. A LLM não cria decisões aprovadas.
3. Afirmações importantes com origem e confiança quando relevante.
4. Questões pendentes visíveis.
5. Exemplos não são requisitos.
6. Orientações de redação não são premissas.
7. Premissas não ocultam requisitos.
8. Conteúdo aprovado alterado exige revisão.
9. Exportações rastreáveis.
10. Importações validadas antes de aplicação.

---

## 21–22. Exemplo e resultado esperado

Ver catálogo de ajuda (`method.example_walkthrough`) e pacote exchange exportado. O método transforma intenção técnica dispersa num **contrato estruturado para desenvolvimento documental assistido por LLM**.

Documento complementar: [GET_APP_SPECIFICATION.md](GET_APP_SPECIFICATION.md).

Diagramas: resumo [GET_METHOD_FLOW.drawio](GET_METHOD_FLOW.drawio); 6 folhas [GET_METHOD_ALL_SHEETS.drawio](GET_METHOD_ALL_SHEETS.drawio). Skills: [GET_SKILLS_OPERATING_MODEL.drawio](GET_SKILLS_OPERATING_MODEL.drawio).

### Roadmap: skills e evolução mínima

- Plano macro (fases F0–F4, M1–M3): [GET_MACRO_PLAN.md](GET_MACRO_PLAN.md)
- Planos micro (F0 ritual, retro): [plans/README.md](plans/README.md)
- Plano de skills (grill, review, decision, research): [GET_SKILLS_PLAN.md](GET_SKILLS_PLAN.md)
- Diagrama de operação: [GET_SKILLS_OPERATING_MODEL.drawio](GET_SKILLS_OPERATING_MODEL.drawio)
- Resumo da análise de evolução do quadro: [GET_FRAMEWORK_EVOLUTION_SUMMARY.md](GET_FRAMEWORK_EVOLUTION_SUMMARY.md)