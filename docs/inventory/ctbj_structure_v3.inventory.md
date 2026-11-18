# Instruções ao Cursor — atualização da estrutura existente GET / CTBJ

## Objetivo
Atualizar diretamente a lista/estrutura inicial atualmente existente no GET para a nova estrutura CTBJ. **Não criar um mecanismo de importação JSON.** Inspecionar o seed/bootstrap/configuração e modelos atuais e alterar apenas o necessário, incluindo migração simples da estrutura já persistida se aplicável.

## Regras de migração
- Preservar conteúdo existente e IDs sempre que exista correspondência semântica segura.
- Em blocos divididos/fundidos, redistribuir conteúdo por significado; conflito ou ambiguidade deve ficar sinalizado para revisão manual, nunca apagado silenciosamente.
- Atualizar códigos, títulos, ordem, fascículos, blocos e pontos de desenvolvimento para F01-F20.
- GET, workflow e processo interno EDA não pertencem ao conteúdo das Especificações Técnicas.
- Arquitetura de referência: PLCs + SCADA, neutralidade de fabricante.
- Historian independente, com hardware/software próprios.
- Redes OT e Cibersegurança OT em fascículos separados.
- WOIS G11/G12 e ABB MicroSCADA integrados via OPC UA; preparar evolução futura da subestação mantendo hardwired onde crítico.
- Source timestamp deve nascer tão perto da origem quanto tecnicamente possível e ser preservado até alarmes/Historian. Para disparos/eventos críticos prever captura por hardware/event task/interrupt PLC quando a precisão o justifique.

## Instrução sobre os pontos de desenvolvimento
Os pontos abaixo não são texto final do CE. São o mapa mínimo de matérias que o GET deve apresentar para cada bloco. Ao atualizar a base atual, manter 5-8 pontos por bloco sempre que a matéria o justificar, evitando pontos genéricos repetidos.

# Estrutura GET CTBJ v3 — inventário de população

**Totais:** 20 fascículos; 179 blocos; 869 pontos de desenvolvimento.

## F01 — Enquadramento e requisitos gerais
### F01_B01 — Objeto e finalidade
- Delimitar a finalidade da remodelação do sistema de comando e controlo da CTBJ.
- Explicitar os resultados operacionais e de engenharia pretendidos.
- Definir a natureza da contratação e o papel do adjudicatário.
- Relacionar o objeto com a continuidade, segurança e modernização da exploração.
### F01_B02 — Caracterização geral da CTBJ e contexto da intervenção
- Caracterizar a central, os grupos e os sistemas comuns abrangidos.
- Descrever o contexto brownfield e a coexistência com instalações em exploração.
- Identificar as principais condicionantes físicas, operacionais e organizacionais.
- Distinguir informação de contexto de requisitos contratuais.
### F01_B03 — Definições, terminologia e abreviaturas
- Estabelecer vocabulário controlado e abreviaturas aplicáveis.
- Distinguir SCADA, PLC, remote I/O, package, sistema externo e sistema autónomo.
- Uniformizar os termos contratação, adjudicatário, EDA e CTBJ.
- Definir termos brownfield, cutover, as-is, as-built, FAT, SAT e OPC UA.
### F01_B04 — Enquadramento normativo, regulamentar e documental
- Identificar legislação, regulamentação, normas e requisitos EDA aplicáveis.
- Definir hierarquia e prevalência entre peças contratuais e documentos técnicos.
- Estabelecer o tratamento de conflitos, omissões e versões normativas.
- Separar requisitos obrigatórios de referências de boa prática.
### F01_B05 — Princípios gerais da solução
- Fixar a arquitetura de referência baseada em PLCs e SCADA.
- Preservar neutralidade de fabricante sem deixar a arquitetura funcional indefinida.
- Estabelecer distribuição do controlo, autonomia local e integração por interfaces abertas.
- Definir princípios de disponibilidade, expansibilidade, manutenção e interoperabilidade.
### F01_B06 — Requisitos gerais da contratação
- Consolidar obrigações gerais de projeto, fornecimento, programação, instalação e ensaio.
- Estabelecer obrigação de levantamento, validação e coordenação pelo adjudicatário.
- Definir requisitos gerais de qualidade, documentação e aprovação pela EDA.
- Evitar duplicar requisitos especializados desenvolvidos nos fascículos próprios.

## F02 — Âmbito, fornecimentos, limites e responsabilidades
### F02_B01 — Âmbito global da contratação
- Delimitar o perímetro técnico e funcional global.
- Incluir substituição integral das remotas abrangidas e implementação do novo SCADA/PLCs.
- Identificar integração dos sistemas existentes e trabalhos de migração.
- Distinguir fornecimento base, opções e trabalhos condicionados.
### F02_B02 — Sistemas e instalações abrangidos
- Inventariar grupos 5 a 10, sistemas comuns, parque de tanques e restantes áreas abrangidas.
- Identificar os grupos 11 e 12, WOIS e MicroSCADA como sistemas a integrar.
- Relacionar cada sistema com os limites físicos e funcionais.
- Controlar inclusões futuras sem alterar informalmente o âmbito.
### F02_B03 — Fornecimentos e trabalhos incluídos
- Detalhar engenharia, hardware, software, programação, instalação, migração e ensaios.
- Incluir licenças, ferramentas, documentação, formação e suporte necessários.
- Definir desmontagem, remoção, reutilização e destino dos equipamentos existentes.
- Cobrir serviços auxiliares necessários à entrega de uma solução funcional.
### F02_B04 — Limites e fronteiras de fornecimento
- Fixar o limite físico nos bornes dos condutores provenientes do campo, salvo exceções aprovadas.
- Definir fronteiras de dados, energia, comunicação e responsabilidade funcional.
- Clarificar limites entre novo sistema, sistemas existentes e fornecimentos de terceiros.
- Exigir registo e aprovação das interfaces e exceções.
### F02_B05 — Matriz de fornecimentos
- Estruturar por item quem fornece, instala, configura, testa e entrega.
- Distinguir equipamentos novos, reutilizados, existentes e de terceiros.
- Relacionar fornecimentos com blocos, sistemas e entregáveis.
- Garantir que não existem componentes necessários sem responsável identificado.
### F02_B06 — Matriz de responsabilidades
- Atribuir responsabilidades de projeto, validação, aprovação, instalação e aceitação.
- Distinguir responsabilidade de execução da autoridade de aprovação da EDA.
- Definir responsabilidades em interfaces e trabalhos coordenados.
- Estabelecer tratamento formal de lacunas e sobreposições.
### F02_B07 — Interfaces e trabalhos de terceiros
- Identificar interfaces com contratos, OEM e intervenções paralelas.
- Obrigar o adjudicatário a coordenar e integrar trabalhos de terceiros dentro do âmbito definido.
- Definir dados, documentação, testes e prazos necessários em cada interface.
- Prever indisponibilidade temporária de sistemas terceiros durante FAT ou migração.
### F02_B08 — Exclusões
- Declarar explicitamente trabalhos e fornecimentos não abrangidos.
- Evitar que exclusões contrariem requisitos necessários ao funcionamento integral.
- Identificar dependências externas associadas a cada exclusão.
- Definir processo para esclarecer omissões antes da execução.
### F02_B09 — Gestão e coordenação de interfaces
- Criar e manter registo/matriz de interfaces.
- Atribuir dono, estado, dependências, decisão e evidência a cada interface.
- Coordenar interfaces técnicas, físicas, funcionais, temporais e documentais.
- Integrar a validação das interfaces nos FAT, SAT e comissionamento.

## F03 — Instalação existente e levantamento as-is
### F03_B01 — Descrição geral da instalação existente
- Descrever os sistemas e áreas existentes relevantes para a contratação.
- Identificar equipamentos em serviço, desativados e previstos para desmontagem.
- Registar limitações de completude e atualidade da informação disponível.
- Fornecer contexto suficiente para planeamento do levantamento.
### F03_B02 — Arquitetura de automação e supervisão existente
- Documentar topologias, PLCs, remotas, SCADA e relações funcionais existentes.
- Incluir arquitetura dos grupos 11 e 12 e respetivo WOIS.
- Incluir arquitetura conhecida da subestação e ABB MicroSCADA.
- Identificar pontos de dependência e single points of failure conhecidos.
### F03_B03 — Inventário de hardware e infraestrutura
- Inventariar PLCs, I/O, servidores, postos, redes, armários e alimentações.
- Registar fabricante, modelo, versão, localização, estado e função quando confirmados.
- Incluir hardware dos grupos 11/12 e sistemas comuns associados.
- Distinguir inventário fornecido pela EDA do inventário validado pelo adjudicatário.
### F03_B04 — Sistemas autónomos e packages existentes
- Identificar packages, controladores proprietários e sistemas autónomos.
- Registar proprietários funcionais, interfaces, protocolos e limitações de acesso.
- Avaliar autonomia e comportamento perante perda de integração.
- Distinguir sistemas a manter, integrar, alterar ou substituir.
### F03_B05 — Listas I/O, datalists e fontes de dados legadas
- Consolidar fontes existentes e remeter listas completas para anexos controlados.
- Avaliar duplicados, inconsistências e normalização atual, incluindo convenções OEM.
- Preservar tags legadas para correlação, sem as reutilizar como modelo novo.
- Registar proveniência, estado de validação e data de cada fonte.
### F03_B06 — Software, lógica, aplicações e configurações existentes
- Inventariar projetos PLC, SCADA, WOIS, MicroSCADA, serviços e dependências.
- Registar versões, licenças, backups, acessos e disponibilidade do source code.
- Identificar lógica crítica, sequências e interfaces que exigem engenharia reversa.
- Definir evidência mínima para considerar uma configuração validada.
### F03_B07 — Documentação técnica existente
- Inventariar desenhos, manuais, listas, atas, pedidos de aprovação e autos de entrega.
- Classificar documentação por sistema, revisão, estado e fiabilidade.
- Incluir documentação histórica relevante dos grupos 11 e 12.
- Definir processo de controlo das lacunas documentais.
### F03_B08 — Levantamento e validação pelo adjudicatário
- Exigir inspeção, levantamento e validação as-is antes da engenharia de detalhe.
- Definir entregáveis, métodos e evidências do levantamento.
- Obrigar à comunicação de divergências antes da intervenção.
- Converter resultados validados em baseline controlada.
### F03_B09 — Condicionantes brownfield
- Definir brownfield no contexto da CTBJ.
- Identificar condicionantes de acesso, paragem, coexistência e segurança operacional.
- Impedir que intervenções afetem sistemas fora do âmbito sem autorização.
- Exigir métodos de trabalho, contingência e reposição compatíveis com instalação em serviço.

## F04 — Migração, faseamento e continuidade operacional
### F04_B01 — Princípios e condicionantes da migração
- Definir migração como disciplina central da solução brownfield.
- Preservar continuidade, segurança e rastreabilidade durante a transição.
- Estabelecer pré-condições e aprovação antes de cada intervenção.
- Relacionar migração com testes, documentação e rollback.
### F04_B02 — Plano obrigatório de faseamento
- Exigir um plano de migração faseado, atualizado e aprovado.
- Organizar fases por sistemas, áreas, grupos e janelas operacionais.
- Definir dependências, recursos, indisponibilidades e critérios de passagem.
- Prever coordenação com exploração e trabalhos de terceiros.
### F04_B03 — Coexistência temporária dos sistemas existente e novo
- Definir arquitetura e regras de coexistência.
- Evitar comandos concorrentes, duplicação de autoridade e estados incoerentes.
- Identificar interfaces temporárias e respetivo ciclo de vida.
- Garantir monitorização e diagnóstico durante a coexistência.
### F04_B04 — Gestão e rastreabilidade da datalist durante a migração
- Atribuir estado controlado a cada sinal ao longo da migração.
- Preservar correlação entre legado, novo tag, origem, destino e evidência de teste.
- Controlar alterações, baselines e discrepâncias.
- Impedir entrada em serviço de sinais sem estado e validação conhecidos.
### F04_B05 — Migração de software, lógica e funções
- Definir método de análise, reimplementação, conversão e validação da lógica.
- Distinguir reprodução funcional de melhorias aprovadas.
- Garantir revisão de interlocks, sequências, setpoints e modos.
- Preservar rastreabilidade entre função existente, requisito e implementação nova.
### F04_B06 — Migração de hardware, sinais e I/O
- Planear substituição de remotas e transferência de sinais.
- Definir desconexão, identificação, ensaio, reconexão e verificação ponto a ponto.
- Controlar alterações de cablagem, bornes, canais e alimentação.
- Prever simulação, bypass autorizado e reposição segura.
### F04_B07 — Cutover
- Definir sequência detalhada, responsabilidades e janela de cutover.
- Estabelecer pré-condições, hold points e critérios go/no-go.
- Integrar testes em campo e confirmação operacional.
- Registar execução, desvios e configuração efetivamente colocada em serviço.
### F04_B08 — Contingência e rollback
- Definir cenários de falha e condições que determinam rollback.
- Garantir backups, materiais, configuração e recursos para reposição.
- Estabelecer tempos, autoridade de decisão e comunicação.
- Testar ou demonstrar a exequibilidade das medidas de contingência.
### F04_B09 — Estabilização e acompanhamento pós-migração
- Definir período e condições de estabilização.
- Monitorizar falhas, alarmes, desempenho e comportamento operacional.
- Corrigir anomalias com controlo de alterações e reteste.
- Estabelecer critérios para encerramento da fase e transferência para operação.

## F05 — Filosofia funcional, modos de operação e alocação do controlo
### F05_B01 — Princípios de controlo
- Definir o âmbito, objetivos e fronteiras de «Princípios de controlo» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Princípios de controlo».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Princípios de controlo».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Princípios de controlo».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Princípios de controlo».
### F05_B02 — Modos de operação
- Definir o âmbito, objetivos e fronteiras de «Modos de operação» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Modos de operação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Modos de operação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Modos de operação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Modos de operação».
### F05_B03 — Controlo local e remoto
- Definir o âmbito, objetivos e fronteiras de «Controlo local e remoto» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Controlo local e remoto».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Controlo local e remoto».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Controlo local e remoto».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Controlo local e remoto».
### F05_B04 — Autoridade e prioridade de comandos
- Definir o âmbito, objetivos e fronteiras de «Autoridade e prioridade de comandos» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Autoridade e prioridade de comandos».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Autoridade e prioridade de comandos».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Autoridade e prioridade de comandos».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Autoridade e prioridade de comandos».
### F05_B05 — Referências e setpoints
- Definir o âmbito, objetivos e fronteiras de «Referências e setpoints» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Referências e setpoints».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Referências e setpoints».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Referências e setpoints».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Referências e setpoints».
### F05_B06 — Estados degradados e fallback
- Definir o âmbito, objetivos e fronteiras de «Estados degradados e fallback» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Estados degradados e fallback».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Estados degradados e fallback».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Estados degradados e fallback».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Estados degradados e fallback».
### F05_B07 — Fail-safe
- Definir o âmbito, objetivos e fronteiras de «Fail-safe» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Fail-safe».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Fail-safe».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Fail-safe».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Fail-safe».
### F05_B08 — Alocação funcional do controlo
- Definir o âmbito, objetivos e fronteiras de «Alocação funcional do controlo» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Alocação funcional do controlo».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Alocação funcional do controlo».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Alocação funcional do controlo».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Alocação funcional do controlo».
### F05_B09 — Funções comuns e coordenação entre sistemas
- Definir o âmbito, objetivos e fronteiras de «Funções comuns e coordenação entre sistemas» no contexto de Filosofia funcional, modos de operação e alocação do controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Funções comuns e coordenação entre sistemas».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Funções comuns e coordenação entre sistemas».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Funções comuns e coordenação entre sistemas».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Funções comuns e coordenação entre sistemas».

## F06 — Automação de processo, PLCs e sistemas de controlo local
### F06_B01 — Arquitetura de automação distribuída
- Definir o âmbito, objetivos e fronteiras de «Arquitetura de automação distribuída» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Arquitetura de automação distribuída».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Arquitetura de automação distribuída».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Arquitetura de automação distribuída».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Arquitetura de automação distribuída».
### F06_B02 — PLCs
- Definir o âmbito, objetivos e fronteiras de «PLCs» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «PLCs».
- Definir interfaces, dependências, responsabilidades e informação necessária para «PLCs».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «PLCs».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «PLCs».
### F06_B03 — Remote I/O e aquisição de sinais
- Definir o âmbito, objetivos e fronteiras de «Remote I/O e aquisição de sinais» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Remote I/O e aquisição de sinais».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Remote I/O e aquisição de sinais».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Remote I/O e aquisição de sinais».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Remote I/O e aquisição de sinais».
### F06_B04 — Aquisição, digitalização e registo temporal de sinais
- Definir aquisição e digitalização por tipo de sinal e criticidade.
- Gerar timestamp tão próximo da origem quanto tecnicamente possível.
- Para alarmes, disparos e sequências críticas, prever captura por hardware, event task ou interrupt no PLC quando necessário.
- Distinguir source timestamp, timestamp do controlador, chegada ao SCADA e inserção no Historian.
- Associar qualidade, resolução, deadband e diagnóstico ao valor adquirido.
- Validar exatidão temporal e ordenação de eventos por ensaio ponta a ponta.
### F06_B05 — Sistemas de controlo local
- Definir o âmbito, objetivos e fronteiras de «Sistemas de controlo local» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Sistemas de controlo local».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Sistemas de controlo local».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Sistemas de controlo local».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Sistemas de controlo local».
### F06_B06 — VFDs e equipamentos inteligentes
- Definir o âmbito, objetivos e fronteiras de «VFDs e equipamentos inteligentes» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «VFDs e equipamentos inteligentes».
- Definir interfaces, dependências, responsabilidades e informação necessária para «VFDs e equipamentos inteligentes».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «VFDs e equipamentos inteligentes».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «VFDs e equipamentos inteligentes».
### F06_B07 — Packages e controladores autónomos
- Definir o âmbito, objetivos e fronteiras de «Packages e controladores autónomos» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Packages e controladores autónomos».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Packages e controladores autónomos».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Packages e controladores autónomos».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Packages e controladores autónomos».
### F06_B08 — Interlocks e interfaces hardwired
- Definir o âmbito, objetivos e fronteiras de «Interlocks e interfaces hardwired» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Interlocks e interfaces hardwired».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Interlocks e interfaces hardwired».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Interlocks e interfaces hardwired».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Interlocks e interfaces hardwired».
### F06_B09 — Disponibilidade e comportamento perante falhas
- Definir o âmbito, objetivos e fronteiras de «Disponibilidade e comportamento perante falhas» no contexto de Automação de processo, PLCs e sistemas de controlo local.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Disponibilidade e comportamento perante falhas».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Disponibilidade e comportamento perante falhas».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Disponibilidade e comportamento perante falhas».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Disponibilidade e comportamento perante falhas».

## F07 — Sistema central SCADA
### F07_B01 — Arquitetura do SCADA
- Definir o âmbito, objetivos e fronteiras de «Arquitetura do SCADA» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Arquitetura do SCADA».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Arquitetura do SCADA».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Arquitetura do SCADA».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Arquitetura do SCADA».
### F07_B02 — Servidores e plataforma de execução
- Definir o âmbito, objetivos e fronteiras de «Servidores e plataforma de execução» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Servidores e plataforma de execução».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Servidores e plataforma de execução».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Servidores e plataforma de execução».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Servidores e plataforma de execução».
### F07_B03 — Postos de operação
- Definir o âmbito, objetivos e fronteiras de «Postos de operação» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Postos de operação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Postos de operação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Postos de operação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Postos de operação».
### F07_B04 — Engineering Workstation
- Definir o âmbito, objetivos e fronteiras de «Engineering Workstation» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Engineering Workstation».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Engineering Workstation».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Engineering Workstation».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Engineering Workstation».
### F07_B05 — Serviços de plataforma
- Definir o âmbito, objetivos e fronteiras de «Serviços de plataforma» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Serviços de plataforma».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Serviços de plataforma».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Serviços de plataforma».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Serviços de plataforma».
### F07_B06 — Redundância e disponibilidade
- Definir o âmbito, objetivos e fronteiras de «Redundância e disponibilidade» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Redundância e disponibilidade».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Redundância e disponibilidade».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Redundância e disponibilidade».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Redundância e disponibilidade».
### F07_B07 — Gestão e configuração da plataforma
- Definir o âmbito, objetivos e fronteiras de «Gestão e configuração da plataforma» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Gestão e configuração da plataforma».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Gestão e configuração da plataforma».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Gestão e configuração da plataforma».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Gestão e configuração da plataforma».
### F07_B08 — Hardware, desempenho e dimensionamento
- Definir o âmbito, objetivos e fronteiras de «Hardware, desempenho e dimensionamento» no contexto de Sistema central SCADA.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Hardware, desempenho e dimensionamento».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Hardware, desempenho e dimensionamento».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Hardware, desempenho e dimensionamento».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Hardware, desempenho e dimensionamento».

## F08 — Modelo de informação, identificação e engenharia de dados
### F08_B01 — Datalist Master
- Definir o âmbito, objetivos e fronteiras de «Datalist Master» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Datalist Master».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Datalist Master».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Datalist Master».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Datalist Master».
### F08_B02 — Modelo de objetos e relações
- Definir o âmbito, objetivos e fronteiras de «Modelo de objetos e relações» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Modelo de objetos e relações».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Modelo de objetos e relações».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Modelo de objetos e relações».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Modelo de objetos e relações».
### F08_B03 — Identificação e classificação de objetos
- Definir o âmbito, objetivos e fronteiras de «Identificação e classificação de objetos» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Identificação e classificação de objetos».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Identificação e classificação de objetos».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Identificação e classificação de objetos».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Identificação e classificação de objetos».
### F08_B04 — Designação semântica dos sinais
- Definir o âmbito, objetivos e fronteiras de «Designação semântica dos sinais» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Designação semântica dos sinais».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Designação semântica dos sinais».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Designação semântica dos sinais».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Designação semântica dos sinais».
### F08_B05 — Modelo físico e mapeamento I/O
- Definir o âmbito, objetivos e fronteiras de «Modelo físico e mapeamento I/O» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Modelo físico e mapeamento I/O».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Modelo físico e mapeamento I/O».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Modelo físico e mapeamento I/O».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Modelo físico e mapeamento I/O».
### F08_B06 — Timestamp, qualidade e origem dos dados
- Modelar value, source timestamp, quality e source/origin como atributos distintos.
- Preservar timestamps recebidos da origem sem os substituir pela hora do servidor.
- Definir comportamento quando a origem não fornece timestamp fiável.
- Registar sincronismo, incerteza, qualidade degradada e dados substituídos.
- Assegurar consistência entre PLC, SCADA, alarmes e Historian.
- Estabelecer critérios de validação temporal para eventos críticos.
### F08_B07 — Dados legados e tabelas de correlação
- Definir o âmbito, objetivos e fronteiras de «Dados legados e tabelas de correlação» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Dados legados e tabelas de correlação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Dados legados e tabelas de correlação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Dados legados e tabelas de correlação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Dados legados e tabelas de correlação».
### F08_B08 — Relações Equipment, PLC, RIO e Instrument
- Definir o âmbito, objetivos e fronteiras de «Relações Equipment, PLC, RIO e Instrument» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Relações Equipment, PLC, RIO e Instrument».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Relações Equipment, PLC, RIO e Instrument».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Relações Equipment, PLC, RIO e Instrument».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Relações Equipment, PLC, RIO e Instrument».
### F08_B09 — Governação, validação e aprovação da datalist
- Definir o âmbito, objetivos e fronteiras de «Governação, validação e aprovação da datalist» no contexto de Modelo de informação, identificação e engenharia de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Governação, validação e aprovação da datalist».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Governação, validação e aprovação da datalist».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Governação, validação e aprovação da datalist».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Governação, validação e aprovação da datalist».

## F09 — Engenharia de software, bibliotecas e funções de controlo
### F09_B01 — Arquitetura e organização do software
- Definir o âmbito, objetivos e fronteiras de «Arquitetura e organização do software» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Arquitetura e organização do software».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Arquitetura e organização do software».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Arquitetura e organização do software».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Arquitetura e organização do software».
### F09_B02 — Regras de programação
- Definir o âmbito, objetivos e fronteiras de «Regras de programação» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Regras de programação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Regras de programação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Regras de programação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Regras de programação».
### F09_B03 — Bibliotecas e blocos funcionais
- Definir o âmbito, objetivos e fronteiras de «Bibliotecas e blocos funcionais» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Bibliotecas e blocos funcionais».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Bibliotecas e blocos funcionais».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Bibliotecas e blocos funcionais».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Bibliotecas e blocos funcionais».
### F09_B04 — Funções standard
- Definir o âmbito, objetivos e fronteiras de «Funções standard» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Funções standard».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Funções standard».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Funções standard».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Funções standard».
### F09_B05 — Sequências e máquinas de estados
- Definir o âmbito, objetivos e fronteiras de «Sequências e máquinas de estados» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Sequências e máquinas de estados».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Sequências e máquinas de estados».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Sequências e máquinas de estados».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Sequências e máquinas de estados».
### F09_B06 — Diagnóstico
- Definir o âmbito, objetivos e fronteiras de «Diagnóstico» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Diagnóstico».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Diagnóstico».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Diagnóstico».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Diagnóstico».
### F09_B07 — Gestão de versões
- Definir o âmbito, objetivos e fronteiras de «Gestão de versões» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Gestão de versões».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Gestão de versões».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Gestão de versões».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Gestão de versões».
### F09_B08 — Documentação do software
- Definir o âmbito, objetivos e fronteiras de «Documentação do software» no contexto de Engenharia de software, bibliotecas e funções de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Documentação do software».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Documentação do software».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Documentação do software».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Documentação do software».

## F10 — HMI, mímicos, operação humana e ergonomia
### F10_B01 — Filosofia HMI e ergonomia
- Definir o âmbito, objetivos e fronteiras de «Filosofia HMI e ergonomia» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Filosofia HMI e ergonomia».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Filosofia HMI e ergonomia».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Filosofia HMI e ergonomia».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Filosofia HMI e ergonomia».
### F10_B02 — Arquitetura de navegação
- Definir o âmbito, objetivos e fronteiras de «Arquitetura de navegação» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Arquitetura de navegação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Arquitetura de navegação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Arquitetura de navegação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Arquitetura de navegação».
### F10_B03 — Mímicos e hierarquia de ecrãs
- Definir o âmbito, objetivos e fronteiras de «Mímicos e hierarquia de ecrãs» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Mímicos e hierarquia de ecrãs».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Mímicos e hierarquia de ecrãs».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Mímicos e hierarquia de ecrãs».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Mímicos e hierarquia de ecrãs».
### F10_B04 — Representação de estados e qualidade
- Definir o âmbito, objetivos e fronteiras de «Representação de estados e qualidade» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Representação de estados e qualidade».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Representação de estados e qualidade».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Representação de estados e qualidade».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Representação de estados e qualidade».
### F10_B05 — Comandos e confirmação do operador
- Definir o âmbito, objetivos e fronteiras de «Comandos e confirmação do operador» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Comandos e confirmação do operador».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Comandos e confirmação do operador».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Comandos e confirmação do operador».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Comandos e confirmação do operador».
### F10_B06 — Tendências e diagnóstico operacional
- Definir o âmbito, objetivos e fronteiras de «Tendências e diagnóstico operacional» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Tendências e diagnóstico operacional».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Tendências e diagnóstico operacional».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Tendências e diagnóstico operacional».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Tendências e diagnóstico operacional».
### F10_B07 — Gestão de utilizadores na HMI
- Definir o âmbito, objetivos e fronteiras de «Gestão de utilizadores na HMI» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Gestão de utilizadores na HMI».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Gestão de utilizadores na HMI».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Gestão de utilizadores na HMI».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Gestão de utilizadores na HMI».
### F10_B08 — Standards gráficos e reutilização
- Definir o âmbito, objetivos e fronteiras de «Standards gráficos e reutilização» no contexto de HMI, mímicos, operação humana e ergonomia.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Standards gráficos e reutilização».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Standards gráficos e reutilização».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Standards gráficos e reutilização».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Standards gráficos e reutilização».

## F11 — Filosofia e gestão de alarmes
### F11_B01 — Filosofia de alarmes
- Definir o âmbito, objetivos e fronteiras de «Filosofia de alarmes» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Filosofia de alarmes».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Filosofia de alarmes».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Filosofia de alarmes».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Filosofia de alarmes».
### F11_B02 — Identificação e classificação de alarmes
- Definir o âmbito, objetivos e fronteiras de «Identificação e classificação de alarmes» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Identificação e classificação de alarmes».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Identificação e classificação de alarmes».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Identificação e classificação de alarmes».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Identificação e classificação de alarmes».
### F11_B03 — Prioridades e racionalização
- Definir o âmbito, objetivos e fronteiras de «Prioridades e racionalização» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Prioridades e racionalização».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Prioridades e racionalização».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Prioridades e racionalização».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Prioridades e racionalização».
### F11_B04 — Geração, timestamp e sequência de eventos
- Definir o âmbito, objetivos e fronteiras de «Geração, timestamp e sequência de eventos» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Geração, timestamp e sequência de eventos».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Geração, timestamp e sequência de eventos».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Geração, timestamp e sequência de eventos».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Geração, timestamp e sequência de eventos».
### F11_B05 — Apresentação e reconhecimento
- Definir o âmbito, objetivos e fronteiras de «Apresentação e reconhecimento» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Apresentação e reconhecimento».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Apresentação e reconhecimento».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Apresentação e reconhecimento».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Apresentação e reconhecimento».
### F11_B06 — Shelving, suppression e estados de manutenção
- Definir o âmbito, objetivos e fronteiras de «Shelving, suppression e estados de manutenção» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Shelving, suppression e estados de manutenção».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Shelving, suppression e estados de manutenção».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Shelving, suppression e estados de manutenção».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Shelving, suppression e estados de manutenção».
### F11_B07 — Histórico, auditoria e análise
- Definir o âmbito, objetivos e fronteiras de «Histórico, auditoria e análise» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Histórico, auditoria e análise».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Histórico, auditoria e análise».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Histórico, auditoria e análise».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Histórico, auditoria e análise».
### F11_B08 — Desempenho e melhoria contínua
- Definir o âmbito, objetivos e fronteiras de «Desempenho e melhoria contínua» no contexto de Filosofia e gestão de alarmes.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Desempenho e melhoria contínua».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Desempenho e melhoria contínua».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Desempenho e melhoria contínua».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Desempenho e melhoria contínua».

## F12 — Sistemas externos, integrações e fronteiras de controlo
### F12_B01 — Princípios de integração
- Definir o âmbito, objetivos e fronteiras de «Princípios de integração» no contexto de Sistemas externos, integrações e fronteiras de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Princípios de integração».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Princípios de integração».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Princípios de integração».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Princípios de integração».
### F12_B02 — G11, G12 e WOIS Wärtsilä
- Caracterizar o WOIS/Wonderware isolado e as funções mantidas.
- Integrar o WOIS no novo SCADA por OPC UA.
- Definir ownership, comandos permitidos, estados, alarmes, timestamps e quality.
- Preservar autonomia e comportamento seguro perante perda de comunicação.
- Incluir PLC do G11, PLC do G12 e PLC dos serviços comuns.
- Prever testes ponta a ponta sem exigir substituição do WOIS.
### F12_B03 — ABB MicroSCADA da subestação
- Tratar o MicroSCADA ABB como sistema autónomo com hardware e software próprios.
- Integrar o MicroSCADA no novo SCADA por OPC UA.
- Identificar os painéis atualmente abrangidos e as lacunas de integração.
- Definir ownership de comandos, estados, alarmes e eventos.
- Preservar autonomia da subestação perante falhas externas.
- Preparar interfaces para a futura expansão do MicroSCADA à totalidade da subestação.
### F12_B04 — Estratégia de evolução da integração da subestação
- Permitir migrar progressivamente sinais de remotas de processo para integração via MicroSCADA/OPC UA.
- Evitar dependências proprietárias desnecessárias na arquitetura do novo SCADA.
- Manter sinais críticos hardwired quando exigido pela função e análise de risco.
- Definir transição, coexistência, correlação e ensaios das duas vias.
- Prever crescimento de namespace, carga, licenças e desempenho.
- Controlar a retirada futura de ligações diretas sem perda funcional.
### F12_B05 — Sinais críticos e interfaces hardwired
- Definir o âmbito, objetivos e fronteiras de «Sinais críticos e interfaces hardwired» no contexto de Sistemas externos, integrações e fronteiras de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Sinais críticos e interfaces hardwired».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Sinais críticos e interfaces hardwired».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Sinais críticos e interfaces hardwired».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Sinais críticos e interfaces hardwired».
### F12_B06 — Integrações OPC UA
- Definir o âmbito, objetivos e fronteiras de «Integrações OPC UA» no contexto de Sistemas externos, integrações e fronteiras de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Integrações OPC UA».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Integrações OPC UA».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Integrações OPC UA».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Integrações OPC UA».
### F12_B07 — Outros sistemas autónomos e packages
- Definir o âmbito, objetivos e fronteiras de «Outros sistemas autónomos e packages» no contexto de Sistemas externos, integrações e fronteiras de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Outros sistemas autónomos e packages».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Outros sistemas autónomos e packages».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Outros sistemas autónomos e packages».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Outros sistemas autónomos e packages».
### F12_B08 — Gestão das fronteiras de controlo
- Definir o âmbito, objetivos e fronteiras de «Gestão das fronteiras de controlo» no contexto de Sistemas externos, integrações e fronteiras de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Gestão das fronteiras de controlo».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Gestão das fronteiras de controlo».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Gestão das fronteiras de controlo».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Gestão das fronteiras de controlo».
### F12_B09 — Perda ou degradação das interfaces
- Definir o âmbito, objetivos e fronteiras de «Perda ou degradação das interfaces» no contexto de Sistemas externos, integrações e fronteiras de controlo.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Perda ou degradação das interfaces».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Perda ou degradação das interfaces».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Perda ou degradação das interfaces».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Perda ou degradação das interfaces».

## F13 — Historian e disponibilização de dados
### F13_B01 — Arquitetura do Historian
- Definir o Historian como sistema independente com hardware e software próprios.
- Delimitar funções face ao SCADA e às integrações corporativas.
- Definir disponibilidade, escalabilidade e retenção sem fixar produto.
- Preservar timestamp e quality da origem.
- Dimensionar fontes, tags, taxas e crescimento com margens justificadas.
- Definir interfaces, segurança e autonomia operacional.
### F13_B02 — Hardware e infraestrutura
- Definir o âmbito, objetivos e fronteiras de «Hardware e infraestrutura» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Hardware e infraestrutura».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Hardware e infraestrutura».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Hardware e infraestrutura».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Hardware e infraestrutura».
### F13_B03 — Software e serviços
- Definir o âmbito, objetivos e fronteiras de «Software e serviços» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Software e serviços».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Software e serviços».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Software e serviços».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Software e serviços».
### F13_B04 — Aquisição e armazenamento
- Definir o âmbito, objetivos e fronteiras de «Aquisição e armazenamento» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Aquisição e armazenamento».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Aquisição e armazenamento».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Aquisição e armazenamento».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Aquisição e armazenamento».
### F13_B05 — Tratamento de timestamps e quality
- Definir o âmbito, objetivos e fronteiras de «Tratamento de timestamps e quality» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Tratamento de timestamps e quality».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Tratamento de timestamps e quality».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Tratamento de timestamps e quality».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Tratamento de timestamps e quality».
### F13_B06 — Retenção e arquivo
- Definir o âmbito, objetivos e fronteiras de «Retenção e arquivo» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Retenção e arquivo».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Retenção e arquivo».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Retenção e arquivo».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Retenção e arquivo».
### F13_B07 — Consulta, tendências e reporting
- Definir o âmbito, objetivos e fronteiras de «Consulta, tendências e reporting» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Consulta, tendências e reporting».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Consulta, tendências e reporting».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Consulta, tendências e reporting».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Consulta, tendências e reporting».
### F13_B08 — Interfaces e disponibilização de dados
- Definir o âmbito, objetivos e fronteiras de «Interfaces e disponibilização de dados» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Interfaces e disponibilização de dados».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Interfaces e disponibilização de dados».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Interfaces e disponibilização de dados».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Interfaces e disponibilização de dados».
### F13_B09 — Integrações corporativas
- Definir o âmbito, objetivos e fronteiras de «Integrações corporativas» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Integrações corporativas».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Integrações corporativas».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Integrações corporativas».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Integrações corporativas».
### F13_B10 — KPI e dados operacionais
- Definir o âmbito, objetivos e fronteiras de «KPI e dados operacionais» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «KPI e dados operacionais».
- Definir interfaces, dependências, responsabilidades e informação necessária para «KPI e dados operacionais».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «KPI e dados operacionais».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «KPI e dados operacionais».
### F13_B11 — Backup, recuperação e disponibilidade
- Definir o âmbito, objetivos e fronteiras de «Backup, recuperação e disponibilidade» no contexto de Historian e disponibilização de dados.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Backup, recuperação e disponibilidade».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Backup, recuperação e disponibilidade».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Backup, recuperação e disponibilidade».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Backup, recuperação e disponibilidade».

## F14 — Redes e comunicações OT
### F14_B01 — Arquitetura de rede OT
- Definir o âmbito, objetivos e fronteiras de «Arquitetura de rede OT» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Arquitetura de rede OT».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Arquitetura de rede OT».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Arquitetura de rede OT».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Arquitetura de rede OT».
### F14_B02 — Switching e routing
- Definir o âmbito, objetivos e fronteiras de «Switching e routing» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Switching e routing».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Switching e routing».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Switching e routing».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Switching e routing».
### F14_B03 — Segmentação lógica
- Definir o âmbito, objetivos e fronteiras de «Segmentação lógica» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Segmentação lógica».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Segmentação lógica».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Segmentação lógica».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Segmentação lógica».
### F14_B04 — Redundância e disponibilidade
- Definir o âmbito, objetivos e fronteiras de «Redundância e disponibilidade» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Redundância e disponibilidade».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Redundância e disponibilidade».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Redundância e disponibilidade».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Redundância e disponibilidade».
### F14_B05 — Redes de automação
- Definir o âmbito, objetivos e fronteiras de «Redes de automação» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Redes de automação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Redes de automação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Redes de automação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Redes de automação».
### F14_B06 — Infraestrutura de comunicação
- Definir o âmbito, objetivos e fronteiras de «Infraestrutura de comunicação» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Infraestrutura de comunicação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Infraestrutura de comunicação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Infraestrutura de comunicação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Infraestrutura de comunicação».
### F14_B07 — Sincronização temporal
- Definir uma referência temporal coerente para PLCs, I/O, SCADA, Historian e sistemas externos.
- Especificar hierarquia, redundância, monitorização e alarmística do serviço de tempo.
- Definir comportamento durante perda ou degradação do sincronismo.
- Garantir que a precisão suporta sequência de eventos e disparos críticos.
- Registar offset, estado de sincronização e qualidade temporal.
- Validar sincronização e propagação de timestamps em FAT e SAT.
### F14_B08 — Diagnóstico e monitorização
- Definir o âmbito, objetivos e fronteiras de «Diagnóstico e monitorização» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Diagnóstico e monitorização».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Diagnóstico e monitorização».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Diagnóstico e monitorização».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Diagnóstico e monitorização».
### F14_B09 — Hardware e dimensionamento
- Definir o âmbito, objetivos e fronteiras de «Hardware e dimensionamento» no contexto de Redes e comunicações OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Hardware e dimensionamento».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Hardware e dimensionamento».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Hardware e dimensionamento».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Hardware e dimensionamento».

## F15 — Cibersegurança OT
### F15_B01 — Princípios e arquitetura de cibersegurança
- Definir o âmbito, objetivos e fronteiras de «Princípios e arquitetura de cibersegurança» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Princípios e arquitetura de cibersegurança».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Princípios e arquitetura de cibersegurança».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Princípios e arquitetura de cibersegurança».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Princípios e arquitetura de cibersegurança».
### F15_B02 — Zonas e conduítes
- Definir o âmbito, objetivos e fronteiras de «Zonas e conduítes» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Zonas e conduítes».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Zonas e conduítes».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Zonas e conduítes».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Zonas e conduítes».
### F15_B03 — Identidades, autenticação e acessos
- Definir o âmbito, objetivos e fronteiras de «Identidades, autenticação e acessos» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Identidades, autenticação e acessos».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Identidades, autenticação e acessos».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Identidades, autenticação e acessos».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Identidades, autenticação e acessos».
### F15_B04 — Hardening
- Definir o âmbito, objetivos e fronteiras de «Hardening» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Hardening».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Hardening».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Hardening».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Hardening».
### F15_B05 — Acesso remoto
- Definir o âmbito, objetivos e fronteiras de «Acesso remoto» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Acesso remoto».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Acesso remoto».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Acesso remoto».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Acesso remoto».
### F15_B06 — Logging e auditoria
- Definir o âmbito, objetivos e fronteiras de «Logging e auditoria» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Logging e auditoria».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Logging e auditoria».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Logging e auditoria».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Logging e auditoria».
### F15_B07 — Atualizações, patches e vulnerabilidades
- Definir o âmbito, objetivos e fronteiras de «Atualizações, patches e vulnerabilidades» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Atualizações, patches e vulnerabilidades».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Atualizações, patches e vulnerabilidades».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Atualizações, patches e vulnerabilidades».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Atualizações, patches e vulnerabilidades».
### F15_B08 — Backup e recovery
- Definir o âmbito, objetivos e fronteiras de «Backup e recovery» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Backup e recovery».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Backup e recovery».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Backup e recovery».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Backup e recovery».
### F15_B09 — Requisitos de componentes e fornecedores
- Definir o âmbito, objetivos e fronteiras de «Requisitos de componentes e fornecedores» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Requisitos de componentes e fornecedores».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Requisitos de componentes e fornecedores».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Requisitos de componentes e fornecedores».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Requisitos de componentes e fornecedores».
### F15_B10 — Gestão ao longo do ciclo de vida
- Definir o âmbito, objetivos e fronteiras de «Gestão ao longo do ciclo de vida» no contexto de Cibersegurança OT.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Gestão ao longo do ciclo de vida».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Gestão ao longo do ciclo de vida».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Gestão ao longo do ciclo de vida».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Gestão ao longo do ciclo de vida».

## F16 — Infraestrutura elétrica, quadros, cablagem e instalação
### F16_B01 — Alimentações
- Definir o âmbito, objetivos e fronteiras de «Alimentações» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Alimentações».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Alimentações».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Alimentações».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Alimentações».
### F16_B02 — UPS e corrente contínua
- Definir o âmbito, objetivos e fronteiras de «UPS e corrente contínua» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «UPS e corrente contínua».
- Definir interfaces, dependências, responsabilidades e informação necessária para «UPS e corrente contínua».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «UPS e corrente contínua».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «UPS e corrente contínua».
### F16_B03 — Quadros, armários e painéis
- Definir o âmbito, objetivos e fronteiras de «Quadros, armários e painéis» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Quadros, armários e painéis».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Quadros, armários e painéis».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Quadros, armários e painéis».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Quadros, armários e painéis».
### F16_B04 — Armários de automação e comunicação
- Definir o âmbito, objetivos e fronteiras de «Armários de automação e comunicação» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Armários de automação e comunicação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Armários de automação e comunicação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Armários de automação e comunicação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Armários de automação e comunicação».
### F16_B05 — Cablagem de controlo e instrumentação
- Definir o âmbito, objetivos e fronteiras de «Cablagem de controlo e instrumentação» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Cablagem de controlo e instrumentação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Cablagem de controlo e instrumentação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Cablagem de controlo e instrumentação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Cablagem de controlo e instrumentação».
### F16_B06 — Fibra ótica e infraestrutura física de comunicações
- Definir o âmbito, objetivos e fronteiras de «Fibra ótica e infraestrutura física de comunicações» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Fibra ótica e infraestrutura física de comunicações».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Fibra ótica e infraestrutura física de comunicações».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Fibra ótica e infraestrutura física de comunicações».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Fibra ótica e infraestrutura física de comunicações».
### F16_B07 — Terras e equipotencialização
- Definir o âmbito, objetivos e fronteiras de «Terras e equipotencialização» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Terras e equipotencialização».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Terras e equipotencialização».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Terras e equipotencialização».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Terras e equipotencialização».
### F16_B08 — EMC e segregação
- Definir o âmbito, objetivos e fronteiras de «EMC e segregação» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «EMC e segregação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «EMC e segregação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «EMC e segregação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «EMC e segregação».
### F16_B09 — Condições ambientais e instalação
- Definir o âmbito, objetivos e fronteiras de «Condições ambientais e instalação» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Condições ambientais e instalação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Condições ambientais e instalação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Condições ambientais e instalação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Condições ambientais e instalação».
### F16_B10 — Identificação física
- Definir o âmbito, objetivos e fronteiras de «Identificação física» no contexto de Infraestrutura elétrica, quadros, cablagem e instalação.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Identificação física».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Identificação física».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Identificação física».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Identificação física».

## F17 — Ensaios, validação, FAT, SAT e comissionamento
### F17_B01 — Estratégia de verificação e validação
- Definir o âmbito, objetivos e fronteiras de «Estratégia de verificação e validação» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Estratégia de verificação e validação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Estratégia de verificação e validação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Estratégia de verificação e validação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Estratégia de verificação e validação».
### F17_B02 — Planos e procedimentos de ensaio
- Definir o âmbito, objetivos e fronteiras de «Planos e procedimentos de ensaio» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Planos e procedimentos de ensaio».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Planos e procedimentos de ensaio».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Planos e procedimentos de ensaio».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Planos e procedimentos de ensaio».
### F17_B03 — FAT
- Definir o âmbito, objetivos e fronteiras de «FAT» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «FAT».
- Definir interfaces, dependências, responsabilidades e informação necessária para «FAT».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «FAT».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «FAT».
### F17_B04 — Testes de integração
- Definir o âmbito, objetivos e fronteiras de «Testes de integração» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Testes de integração».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Testes de integração».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Testes de integração».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Testes de integração».
### F17_B05 — SAT
- Definir o âmbito, objetivos e fronteiras de «SAT» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «SAT».
- Definir interfaces, dependências, responsabilidades e informação necessária para «SAT».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «SAT».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «SAT».
### F17_B06 — Testes funcionais e de desempenho
- Definir o âmbito, objetivos e fronteiras de «Testes funcionais e de desempenho» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Testes funcionais e de desempenho».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Testes funcionais e de desempenho».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Testes funcionais e de desempenho».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Testes funcionais e de desempenho».
### F17_B07 — Testes de disponibilidade e falha
- Definir o âmbito, objetivos e fronteiras de «Testes de disponibilidade e falha» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Testes de disponibilidade e falha».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Testes de disponibilidade e falha».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Testes de disponibilidade e falha».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Testes de disponibilidade e falha».
### F17_B08 — Comissionamento
- Definir o âmbito, objetivos e fronteiras de «Comissionamento» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Comissionamento».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Comissionamento».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Comissionamento».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Comissionamento».
### F17_B09 — Pendentes e critérios de aceitação
- Definir o âmbito, objetivos e fronteiras de «Pendentes e critérios de aceitação» no contexto de Ensaios, validação, FAT, SAT e comissionamento.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Pendentes e critérios de aceitação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Pendentes e critérios de aceitação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Pendentes e critérios de aceitação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Pendentes e critérios de aceitação».

## F18 — Entregáveis, documentação, formação e ciclo de vida
### F18_B01 — Entregáveis de engenharia
- Definir o âmbito, objetivos e fronteiras de «Entregáveis de engenharia» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Entregáveis de engenharia».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Entregáveis de engenharia».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Entregáveis de engenharia».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Entregáveis de engenharia».
### F18_B02 — Documentação as-built
- Definir o âmbito, objetivos e fronteiras de «Documentação as-built» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Documentação as-built».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Documentação as-built».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Documentação as-built».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Documentação as-built».
### F18_B03 — Source code e projetos editáveis
- Definir o âmbito, objetivos e fronteiras de «Source code e projetos editáveis» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Source code e projetos editáveis».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Source code e projetos editáveis».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Source code e projetos editáveis».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Source code e projetos editáveis».
### F18_B04 — Configurações e backups
- Definir o âmbito, objetivos e fronteiras de «Configurações e backups» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Configurações e backups».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Configurações e backups».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Configurações e backups».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Configurações e backups».
### F18_B05 — Software, firmware e ferramentas de engenharia
- Definir o âmbito, objetivos e fronteiras de «Software, firmware e ferramentas de engenharia» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Software, firmware e ferramentas de engenharia».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Software, firmware e ferramentas de engenharia».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Software, firmware e ferramentas de engenharia».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Software, firmware e ferramentas de engenharia».
### F18_B06 — Licenças e direitos de utilização
- Definir o âmbito, objetivos e fronteiras de «Licenças e direitos de utilização» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Licenças e direitos de utilização».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Licenças e direitos de utilização».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Licenças e direitos de utilização».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Licenças e direitos de utilização».
### F18_B07 — Formação
- Definir o âmbito, objetivos e fronteiras de «Formação» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Formação».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Formação».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Formação».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Formação».
### F18_B08 — Sobressalentes
- Definir o âmbito, objetivos e fronteiras de «Sobressalentes» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Sobressalentes».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Sobressalentes».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Sobressalentes».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Sobressalentes».
### F18_B09 — Suporte e garantia
- Definir o âmbito, objetivos e fronteiras de «Suporte e garantia» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Suporte e garantia».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Suporte e garantia».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Suporte e garantia».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Suporte e garantia».
### F18_B10 — Obsolescência e ciclo de vida
- Definir o âmbito, objetivos e fronteiras de «Obsolescência e ciclo de vida» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Obsolescência e ciclo de vida».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Obsolescência e ciclo de vida».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Obsolescência e ciclo de vida».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Obsolescência e ciclo de vida».
### F18_B11 — Entrega técnica final
- Definir o âmbito, objetivos e fronteiras de «Entrega técnica final» no contexto de Entregáveis, documentação, formação e ciclo de vida.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Entrega técnica final».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Entrega técnica final».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Entrega técnica final».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Entrega técnica final».

## F19 — Gestão da contratação e qualidade
### F19_B01 — Organização e gestão
- Definir o âmbito, objetivos e fronteiras de «Organização e gestão» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Organização e gestão».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Organização e gestão».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Organização e gestão».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Organização e gestão».
### F19_B02 — Planeamento e progresso
- Definir o âmbito, objetivos e fronteiras de «Planeamento e progresso» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Planeamento e progresso».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Planeamento e progresso».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Planeamento e progresso».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Planeamento e progresso».
### F19_B03 — Document register e submittals
- Definir o âmbito, objetivos e fronteiras de «Document register e submittals» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Document register e submittals».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Document register e submittals».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Document register e submittals».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Document register e submittals».
### F19_B04 — Revisão e aprovação documental
- Definir o âmbito, objetivos e fronteiras de «Revisão e aprovação documental» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Revisão e aprovação documental».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Revisão e aprovação documental».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Revisão e aprovação documental».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Revisão e aprovação documental».
### F19_B05 — QA e QC
- Definir o âmbito, objetivos e fronteiras de «QA e QC» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «QA e QC».
- Definir interfaces, dependências, responsabilidades e informação necessária para «QA e QC».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «QA e QC».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «QA e QC».
### F19_B06 — Gestão de alterações
- Definir o âmbito, objetivos e fronteiras de «Gestão de alterações» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Gestão de alterações».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Gestão de alterações».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Gestão de alterações».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Gestão de alterações».
### F19_B07 — Não conformidades e NCR
- Definir o âmbito, objetivos e fronteiras de «Não conformidades e NCR» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Não conformidades e NCR».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Não conformidades e NCR».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Não conformidades e NCR».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Não conformidades e NCR».
### F19_B08 — Coordenação de interfaces
- Definir o âmbito, objetivos e fronteiras de «Coordenação de interfaces» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Coordenação de interfaces».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Coordenação de interfaces».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Coordenação de interfaces».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Coordenação de interfaces».
### F19_B09 — Reuniões e reporting
- Definir o âmbito, objetivos e fronteiras de «Reuniões e reporting» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Reuniões e reporting».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Reuniões e reporting».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Reuniões e reporting».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Reuniões e reporting».
### F19_B10 — Receção provisória e definitiva
- Definir o âmbito, objetivos e fronteiras de «Receção provisória e definitiva» no contexto de Gestão da contratação e qualidade.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Receção provisória e definitiva».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Receção provisória e definitiva».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Receção provisória e definitiva».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Receção provisória e definitiva».

## F20 — Segurança e Saúde no Trabalho durante a execução
### F20_B01 — Objeto e princípios gerais
- Definir o âmbito, objetivos e fronteiras de «Objeto e princípios gerais» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Objeto e princípios gerais».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Objeto e princípios gerais».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Objeto e princípios gerais».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Objeto e princípios gerais».
### F20_B02 — Responsabilidades do adjudicatário
- Definir o âmbito, objetivos e fronteiras de «Responsabilidades do adjudicatário» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Responsabilidades do adjudicatário».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Responsabilidades do adjudicatário».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Responsabilidades do adjudicatário».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Responsabilidades do adjudicatário».
### F20_B03 — Acesso e permanência na CTBJ
- Definir o âmbito, objetivos e fronteiras de «Acesso e permanência na CTBJ» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Acesso e permanência na CTBJ».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Acesso e permanência na CTBJ».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Acesso e permanência na CTBJ».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Acesso e permanência na CTBJ».
### F20_B04 — Coordenação com a exploração
- Definir o âmbito, objetivos e fronteiras de «Coordenação com a exploração» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Coordenação com a exploração».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Coordenação com a exploração».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Coordenação com a exploração».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Coordenação com a exploração».
### F20_B05 — Autorizações, consignações e trabalhos elétricos
- Definir o âmbito, objetivos e fronteiras de «Autorizações, consignações e trabalhos elétricos» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Autorizações, consignações e trabalhos elétricos».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Autorizações, consignações e trabalhos elétricos».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Autorizações, consignações e trabalhos elétricos».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Autorizações, consignações e trabalhos elétricos».
### F20_B06 — Trabalhos em instalações e sistemas em serviço
- Definir o âmbito, objetivos e fronteiras de «Trabalhos em instalações e sistemas em serviço» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Trabalhos em instalações e sistemas em serviço».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Trabalhos em instalações e sistemas em serviço».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Trabalhos em instalações e sistemas em serviço».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Trabalhos em instalações e sistemas em serviço».
### F20_B07 — Emergência e comunicação de ocorrências
- Definir o âmbito, objetivos e fronteiras de «Emergência e comunicação de ocorrências» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Emergência e comunicação de ocorrências».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Emergência e comunicação de ocorrências».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Emergência e comunicação de ocorrências».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Emergência e comunicação de ocorrências».
### F20_B08 — Organização, limpeza e reposição das áreas
- Definir o âmbito, objetivos e fronteiras de «Organização, limpeza e reposição das áreas» no contexto de Segurança e Saúde no Trabalho durante a execução.
- Identificar requisitos funcionais, técnicos e de desempenho aplicáveis a «Organização, limpeza e reposição das áreas».
- Definir interfaces, dependências, responsabilidades e informação necessária para «Organização, limpeza e reposição das áreas».
- Estabelecer entregáveis, evidências, critérios de verificação e aceitação de «Organização, limpeza e reposição das áreas».
- Registar condicionantes brownfield, estados degradados e situações de exceção relevantes para «Organização, limpeza e reposição das áreas».

## Complementos obrigatórios aos pontos de desenvolvimento

Além da lista abaixo, enriquecer especificamente os blocos indicados, substituindo pontos genéricos equivalentes quando existam:

### F06_B04 — Aquisição, digitalização e registo temporal de sinais
- Cadeia completa sensor/contacto → I/O → PLC → SCADA → Historian.
- Filtragem, debounce, scan/update, resolução e deadband conforme natureza do sinal.
- Source timestamp gerado tão próximo da origem quanto possível.
- Para trip/alarmes/eventos críticos usar captura por I/O, event task, interrupt PLC ou equivalente quando necessário.
- Distinguir source timestamp, controller timestamp, receive time e historian insert time.
- Propagar quality/validity e diagnóstico.
- Verificar precisão e sequence-of-events ponta a ponta em FAT/SAT.

### F08_B01/B06 — Datalist e temporalidade
- Datalist como fonte mestre controlada, com estados de maturidade, ownership e baseline.
- Separar identificação do objeto, semântica do sinal e implementação física.
- Modelar value + source timestamp + quality + source/origin.
- Nunca substituir timestamp válido de origem pela hora do servidor.
- Manter correlação legacy tag ↔ objeto novo ↔ signal name novo.
- Validar consistência temporal entre PLC, SCADA, alarmes e Historian.

### F11 — Alarmes
- Distinguir alarme, evento e estado.
- Racionalização e prioridade baseada em consequência/resposta do operador.
- Source timestamp para ordenação de eventos críticos.
- SOE com precisão suficiente para reconstruir disparos.
- Shelving/suppression controlado e auditável.
- Standing/chattering/nuisance alarms e alarm floods.
- Histórico com ocorrência, reconhecimento, retorno e timestamp preservado.

### F12_B02 — G11/G12 e WOIS Wärtsilä
- WOIS/Wonderware permanece sistema autónomo.
- Integração no novo SCADA via OPC UA.
- Considerar PLC G11, PLC G12 e PLC dos serviços comuns.
- Definir ownership de comandos, estados, alarmes, referências, timestamp e quality.
- Definir comportamento seguro perante perda OPC UA.
- Testar recuperação e integração ponta a ponta.

### F12_B03/B04 — ABB MicroSCADA / subestação
- MicroSCADA permanece sistema independente com hardware/software próprios.
- Integração no novo SCADA via OPC UA.
- Inventariar painéis/IED já abrangidos e sinais ainda adquiridos diretamente por remotas de processo.
- Preparar expansão futura do MicroSCADA à totalidade da subestação.
- Permitir alteração futura da origem do sinal sem alterar a sua identidade/semântica.
- Prever coexistência temporária entre aquisição direta e OPC UA.
- Manter sinais críticos hardwired quando funcionalmente necessário.
- Preservar timestamps originados na subestação.

### F13 — Historian
- Sistema autónomo, com servidores/storage/software/licenças próprios.
- Dimensionar tags, sampling, retenção, crescimento e disponibilidade.
- Preservar source timestamp e quality.
- Definir buffering/store-and-forward para interrupções relevantes.
- Diferenciar source time de receive/insert time.
- Definir retenção, arquivo, consulta, reporting e exportação.
- Definir interfaces OT/IT sem criar dependência do Historian para controlo em tempo real.
- Definir backup, restore e teste de recuperação.

### F14_B07 — Sincronização temporal
- Fonte temporal coerente para PLCs, I/O, SCADA, Historian e sistemas externos.
- Definir protocolo segundo precisão necessária.
- Hierarquia/redundância de fontes de tempo.
- Monitorizar offset, estado e qualidade do sincronismo.
- Definir degradação/perda de sincronismo.
- Precisão compatível com SOE/trips críticos.
- Testar sincronização em FAT/SAT.

### F17 — Ensaios
- Rastrear requisitos para método/evidência de verificação.
- FAT de PLC, SCADA, HMI, alarmes, interfaces e falhas.
- SAT com point-to-point/loop checks e sinais reais.
- Testes de WOIS e MicroSCADA via OPC UA.
- Testar source timestamp/quality ponta a ponta e ordenação SOE.
- Testar failover, perda/recuperação de comunicação e estados degradados.
- Retestar após correções que afetem resultados anteriores.
- Punch list/NCR e critérios objetivos de aceitação.

### F20 — HST
- Manter proporcional ao trabalho efetivo desta empreitada.
- Cumprir legislação aplicável e procedimentos/requisitos EDA/INOVS.
- Acesso/permanência e coordenação com exploração.
- Autorizações, consignações e trabalhos elétricos.
- Trabalhos em sistemas/instalações em serviço.
- Emergência e comunicação de ocorrências.
- Organização, limpeza e reposição das áreas.
- Não adicionar requisitos artificiais de gruas/grandes movimentações quando não aplicáveis.

## Execução pelo Cursor
1. Localizar a definição da estrutura inicial e os modelos persistentes.
2. Fazer backup da base atual.
3. Implementar a nova árvore e pontos diretamente nas estruturas existentes.
4. Criar migração idempotente apenas se a base já persistida necessitar atualização.
5. Preservar conteúdos existentes e produzir relatório de conflitos.
6. Verificar que a UI apresenta F01-F20 e todos os blocos na ordem definida.
7. Verificar edição normal dos novos pontos de desenvolvimento.
8. Correr testes existentes; não fazer refatorações não relacionadas.
9. Reportar ficheiros alterados, migração executada, conteúdos preservados e itens que requerem revisão manual.
