# ADR-0006: Login opcional e preservação da conversa anônima

- **Status:** Aceita
- **Data:** 2026-10-29
- **Origem:** Decisão de produto já registrada nas seções 12 e 88 do
  [overview técnico](../../OVERVIEW%20T%C3%89CNICO.md), reafirmada na integração do frontend.

## Contexto

O chat deve ser acessível sem cadastro. O backend inicial de conversas exigia
um usuário autenticado; copiar essa restrição para a interface colocou um
formulário de login no lugar da conversa e contrariou a decisão de produto.

## Decisão

- O botão Entrar fica nos headers da landing e do chat. O formulário abre em um
  diálogo separado, sem substituir as mensagens nem apagar o rascunho.
- O visitante pode começar imediatamente. Uma sessão anônima permite inicialmente
  3 perguntas e expira em aproximadamente 4 horas. Esses valores são configuráveis
  por `ANONYMOUS_QUESTIONS_LIMIT` e `ANONYMOUS_SESSION_MINUTES`.
- O backend emite um token aleatório e persiste apenas seu hash SHA-256. O Next
  mantém o token em cookie HttpOnly, SameSite=Lax e Secure em produção e envia
  `X-Anonymous-Token` ao backend. O cliente recebe somente quota e expiração.
- Cada conversa pertence exclusivamente a uma conta ou a uma sessão anônima.
  A autorização é verificada no backend para leitura e envio, com o mesmo 404
  para conversa inexistente ou pertencente a outra pessoa.
- A reserva de quota usa UPDATE condicional no banco. Perguntas inválidas e
  falhas de geração não consomem a quota; não há repetição automática de POST.
- Login ou cadastro transfere as conversas da sessão válida para a conta em
  uma transação, remove o vínculo anônimo e invalida o token temporário.
  IDs, mensagens e citações permanecem os mesmos. Nenhum histórico é copiado.
- Esgotar a quota impede novos envios anônimos, sem esconder o histórico nem
  impor uma tela de login. Entrar continua sendo uma ação explícita.

## Consequências e limites desta implementação

É necessária a migration `anonymous_sessions_01`. O teste isolado usa FastAPI
real com SQLite e RAG substituído, cobrindo quota, isolamento, expiração,
cadastro/login e preservação dos dados. A validação com PostgreSQL e IA reais
permanece uma verificação de ambiente separada.

O overview também prevê rate limiting adicional por IP, limpeza automática da
retenção, quota diária de contas, classificação de escopo e refresh tokens com
rotação. Esses mecanismos ainda não estão implementados nesta fatia. A quota
atual vale por token de sessão; apagar o cookie pode iniciar outra sessão.
Não se deve confundir esse limite com proteção completa contra abuso público.

O JWT de acesso existente continua sendo validado pelo FastAPI, com cookie
HttpOnly no Next e sem refresh/revogação no backend. Essa limitação não torna
o login obrigatório para iniciar a conversa.
