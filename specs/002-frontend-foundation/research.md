# Research: Fundação do Frontend

## Decision: usar App Router com fronteira explícita entre servidor e cliente

**Rationale**: Páginas e layouts não interativos permanecem no servidor por padrão; somente chat, formulários, popovers, provedores de query e controles de tema precisam de interação no browser. A documentação atual do Next.js reforça que componentes cliente devem seguir as mesmas premissas de segurança do browser e não podem acessar dados ou módulos privilegiados.

**Alternatives considered**:

- Transformar toda página em componente cliente: rejeitado por aumentar JavaScript, misturar responsabilidades e reduzir a fronteira de segurança.
- Usar pages router: rejeitado pois o projeto já parte de uma arquitetura nova e não possui legado que justifique essa escolha.

## Decision: expor no browser apenas configuração pública

**Rationale**: No Next.js, variáveis com prefixo `NEXT_PUBLIC_` são incluídas no bundle durante a build. Portanto, apenas a base URL pública da API e valores equivalentes podem receber esse prefixo. Tokens, credenciais de provedores e qualquer segredo não entram no bundle.

**Alternatives considered**:

- Colocar token ou credencial da API em variável pública: rejeitado por expor segredo ao navegador.
- Fazer o browser conhecer todos os segredos por conveniência: rejeitado por violar a fronteira de segurança.

## Decision: estado remoto separado de estado efêmero de interação

**Rationale**: Conversas, mensagens persistidas, detalhes de citações e documentos são cópias cacheadas de dados do servidor, com invalidação após mutações. Rascunho, abertura da sidebar e conteúdo parcial de streaming têm ciclo de vida de interface e não devem ser tratados como dados persistidos. Essa separação reduz duplicidade e inconsistência.

**Alternatives considered**:

- Uma store global para tudo: rejeitado porque mistura cache, UI e estado de rede.
- Estado local para tudo: rejeitado porque sidebar, histórico e citação podem atravessar componentes e rotas.

## Decision: integrar SSE por um adaptador testável

**Rationale**: O overview prevê `status`, `text`, `sources`, `done` e `error`. Um adaptador converte os eventos em uma mensagem de interface e permite testes determinísticos de cada sequência, inclusive interrupção e falha. O frontend não interpreta dados internos do RAG.

**Alternatives considered**:

- Conectar o componente visual diretamente ao stream: rejeitado por dificultar cancelamento, testes e tratamento de estados terminais.
- Usar `EventSource`: rejeitado porque é restrito a GET e não transporta o `POST` de mensagem planejado com cabeçalhos de autorização personalizados.
- Usar WebSocket: rejeitado porque a arquitetura do projeto especifica SSE.

## Decision: usar detalhe de citação sob demanda como primeiro contrato real

**Rationale**: `GET /api/v1/citations/{id}` já existe e retorna o número, trecho original, chunk e fonte. É suficiente para validar a experiência de confiança com fixtures de mensagem enquanto o endpoint de chat não é entregue.

**Alternatives considered**:

- Exibir uma fonte genérica sem consultar evidência: rejeitado pois contraria rastreabilidade.
- Receber IDs internos de chunk no frontend: rejeitado explicitamente pela arquitetura do projeto.
