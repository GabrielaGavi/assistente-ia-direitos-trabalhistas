# Feature Specification: Fundação do Frontend

**Feature Branch**: `002-frontend-foundation`  
**Created**: 2026-10-27  
**Status**: Draft  
**Input**: Criar a arquitetura inicial do frontend para o Assistente Inteligente de Orientação sobre Direitos Trabalhistas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fazer uma pergunta com segurança (Priority: P1)

Como trabalhador, quero iniciar uma conversa e enviar uma dúvida trabalhista em linguagem simples para receber uma orientação informativa acompanhada de evidências, sem confundir a ferramenta com aconselhamento jurídico profissional.

**Why this priority**: Esta é a entrega de maior valor do produto e torna o mecanismo de conhecimento acessível ao público-alvo.

**Independent Test**: Uma pessoa abre a área de conversa, entende o aviso de uso, envia uma pergunta válida e acompanha todos os estados da resposta até sua conclusão ou falha.

**Acceptance Scenarios**:

1. **Given** que a pessoa acessa o produto pela primeira vez, **When** inicia uma conversa, **Then** ela encontra o propósito da ferramenta, o aviso de caráter informativo e um campo de pergunta claramente identificado.
2. **Given** que há uma resposta em elaboração, **When** a pessoa acompanha a conversa, **Then** ela recebe retorno de progresso e pode interromper a geração.
3. **Given** que não há evidência suficiente para responder, **When** a resposta é concluída, **Then** a interface informa a limitação sem apresentar uma conclusão jurídica especulativa.

---

### User Story 2 - Conferir uma fonte citada (Priority: P1)

Como trabalhador, quero abrir uma citação presente na resposta para conferir o trecho original, sua identificação e o link oficial antes de confiar na orientação recebida.

**Why this priority**: Rastreabilidade é requisito de confiança do produto e reduz o risco de a interface apresentar uma resposta de IA como verdade sem fundamento.

**Independent Test**: Dada uma mensagem respondida com citação, a pessoa aciona a referência e visualiza o trecho literal e a origem oficial sem sair da conversa; consegue também abrir a fonte em nova aba.

**Acceptance Scenarios**:

1. **Given** uma resposta com uma ou mais referências numéricas, **When** a pessoa seleciona uma referência, **Then** vê número, organização, título, trecho literal, identificação normativa disponível e link oficial.
2. **Given** que a evidência não possa ser carregada, **When** a pessoa abre a referência, **Then** recebe uma mensagem clara de falha e mantém a resposta da conversa disponível.

---

### User Story 3 - Retomar uma conversa (Priority: P2)

Como usuário recorrente, quero criar, abrir, renomear e excluir conversas pelo histórico para continuar uma dúvida sem repetir todo o contexto.

**Why this priority**: O histórico melhora a continuidade de uso, mas o chat utilizável e rastreável continua sendo a primeira entrega independente.

**Independent Test**: Com conversas disponíveis, a pessoa abre uma conversa anterior, confirma suas mensagens, cria outra e executa as operações de organização previstas.

**Acceptance Scenarios**:

1. **Given** que existem conversas acessíveis ao usuário, **When** ele abre uma conversa no histórico, **Then** vê as mensagens na ordem original e pode continuar a conversa.
2. **Given** uma conversa no histórico, **When** o usuário solicita renomeá-la ou excluí-la, **Then** recebe confirmação do resultado e o histórico é atualizado sem recarregar a página.

---

### User Story 4 - Administrar a base de conhecimento (Priority: P3)

Como administrador autorizado, quero consultar fontes e documentos, acompanhar processamento e alterar o estado dos documentos para manter a base de conhecimento controlada.

**Why this priority**: É necessário para operação e qualidade da base, mas depende dos fluxos administrativos ainda não expostos pelo backend.

**Independent Test**: Um administrador autorizado acessa a área administrativa e consegue distinguir fontes, documentos, seus estados e as ações disponíveis para cada um.

**Acceptance Scenarios**:

1. **Given** um usuário sem autorização administrativa, **When** tenta acessar a área administrativa, **Then** não visualiza dados nem ações administrativas.
2. **Given** um administrador autorizado, **When** consulta a base, **Then** identifica os estados de cada documento e obtém retorno visível para as ações permitidas.

### Edge Cases

- A conexão pode cair ou a geração pode terminar com erro depois de parte do texto já ter sido exibida; o texto recebido deve permanecer distinguível de uma resposta concluída.
- A pessoa pode tentar enviar uma segunda pergunta enquanto uma resposta da mesma conversa está em andamento; a interface deve evitar envios concorrentes e explicar o estado.
- Uma resposta pode não possuir citação por insuficiência de evidências ou por mensagem fora de escopo; a ausência precisa ser explícita, sem referência quebrada.
- O histórico, uma citação ou uma ação administrativa pode retornar ausência de permissão, item inexistente ou falha de rede; a interface deve informar o próximo passo sem expor detalhes internos.
- Em telas pequenas, navegação, leitura da resposta e acesso às fontes devem permanecer possíveis por teclado e leitor de tela.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A aplicação DEVE apresentar uma área conversacional acessível que permita iniciar uma conversa e enviar uma pergunta de texto.
- **FR-002**: A aplicação DEVE mostrar, antes e durante o uso do chat, que as orientações são informativas e não substituem atendimento jurídico profissional.
- **FR-003**: A aplicação DEVE exibir progresso, conclusão, interrupção e falha da elaboração de resposta de forma compreensível e não ambígua.
- **FR-004**: A aplicação DEVE renderizar a resposta com formatação segura, sem executar conteúdo arbitrário originado na resposta.
- **FR-005**: A aplicação DEVE tornar cada citação da resposta acionável e apresentar sua evidência original, metadados disponíveis e link oficial quando fornecidos.
- **FR-006**: A aplicação DEVE preservar o texto original da evidência ao exibi-la; pode resumir visualmente apenas com uma ação explícita para expandir.
- **FR-007**: A aplicação DEVE diferenciar visualmente uma resposta fundamentada de uma resposta com evidência insuficiente, fora de escopo ou erro.
- **FR-008**: A aplicação DEVE impedir o envio concorrente de mensagens na mesma conversa enquanto uma resposta estiver em elaboração e permitir solicitar sua interrupção.
- **FR-009**: A aplicação DEVE permitir criar, abrir, renomear e excluir conversas quando esses recursos estiverem disponíveis para a sessão do usuário.
- **FR-010**: A aplicação DEVE manter o estado do servidor atualizado após operações de conversa, citação ou administração, sem exigir recarregamento completo da página.
- **FR-011**: A aplicação DEVE oferecer interface responsiva, com navegação por teclado, foco visível, rótulos semânticos, contraste adequado e mensagens de erro anunciáveis por tecnologias assistivas.
- **FR-012**: A aplicação DEVE disponibilizar tema claro e escuro sem comprometer legibilidade ou os requisitos de acessibilidade.
- **FR-013**: A aplicação DEVE reservar uma área administrativa apenas para usuários autorizados, apresentando fontes, documentos e seus estados sem expor controles a usuários não autorizados.
- **FR-014**: A aplicação DEVE tratar indisponibilidade, expiração de sessão e respostas de erro do serviço com mensagens em linguagem simples e uma ação de recuperação quando aplicável.

### Key Entities

- **Conversa**: Contexto organizado de perguntas e respostas de uma pessoa, com identificação, título, situação e mensagens ordenadas.
- **Mensagem**: Pergunta de uma pessoa ou resposta do assistente, incluindo seu conteúdo, situação de geração e referências associadas.
- **Citação**: Evidência verificável ligada a uma resposta, com numeração, trecho literal, origem documental e links oficiais.
- **Fonte**: Organização ou repositório oficial de origem de documentos usados como evidência.
- **Documento**: Material normativo versionado, associado a uma fonte e com estado de disponibilidade para a base de conhecimento.
- **Sessão de usuário**: Contexto de acesso que define se a pessoa usa o produto de modo anônimo, autenticado ou administrativo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em teste de usabilidade com cinco pessoas do público-alvo, pelo menos quatro conseguem enviar uma primeira dúvida e identificar o caráter informativo da ferramenta sem auxílio.
- **SC-002**: Em cenários com respostas citadas, 100% das referências exibidas abrem uma evidência correspondente ou mostram uma falha explícita, sem links quebrados silenciosos.
- **SC-003**: Em testes de navegação por teclado dos fluxos de chat e citação, todas as ações interativas são alcançáveis, possuem foco visível e podem ser concluídas sem mouse.
- **SC-004**: Em viewport de 320 pixels de largura e em desktop, os fluxos de primeira pergunta, leitura de resposta e consulta de fonte são concluídos sem rolagem horizontal da página.
- **SC-005**: Em simulações de progresso, erro, interrupção e evidência insuficiente, 100% dos estados exibem uma mensagem de situação compreensível e uma ação disponível quando há recuperação possível.

## Assumptions

- O primeiro corte de interface prioriza chat, citações e histórico; autenticação e administração entram de forma incremental conforme os contratos do backend forem disponibilizados.
- A sessão pode começar de maneira anônima e evoluir para uma conta autenticada sem mudar o comportamento básico de perguntas e evidências.
- As respostas recebem referências no formato numérico e a interface consulta detalhes de uma referência por seu identificador público, nunca por identificadores internos de trechos.
- Os contratos de conversa, autenticação, streaming, interrupção, regeneração e administração ainda precisam ser formalizados pelo backend antes de sua integração real.
- O conteúdo legal e os links oficiais são de responsabilidade do backend; a interface não interpreta nem inventa informação jurídica.
