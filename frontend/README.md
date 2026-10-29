# Frontend — Direito em claro

```bash
pnpm install --frozen-lockfile
pnpm dev
```

Abra http://localhost:3000. Para validar uma versão de produção:

```bash
pnpm lint
pnpm exec tsc --noEmit
pnpm build
pnpm start
```

A rota `/` usa `src/components/landing/direito-site.tsx` e seu CSS Module.
O hero alterna texto e grafo; os efeitos de pontos e esfera usam canvas.
O campo de pixels do hero usa a estátua WebP apenas como mapa de referência:
quadrados individuais formam o rosto por tamanho e luminância, sem exibir a foto.
As animações param fora da tela e respeitam
movimento reduzido. A arquitetura distingue módulos existentes e planejados.

Os temas são definidos em `src/lib/chat-topics.ts`. Os links carregam o tema
e a pergunta em `/chat?tema=...&q=...`; `chat-entry.tsx` preenche o rascunho,
sem enviá-lo automaticamente. O chat usa CSS Module e uma grade de altura
limitada à viewport: cabeçalho, conversa rolável e compositor independente.

Lenis roda no ticker do GSAP: no documento para a landing e no contêiner da
conversa para o chat. As instâncias são destruídas ao sair de cada rota.
O FAQ anima a altura de cada painel com GSAP, inclusive ao fechar.

Fontes locais ficam em `public/fonts/` e `src/app/fonts/`. A estátua convertida
fica em `public/assets/statue-head.webp`. Os arquivos antigos de referência
não são dependências do desenvolvimento ou do build. Não há geração de HTML
nem cópia de bibliotecas para `public/vendor`.

O layout compartilhado usa `next/font/local` com as mesmas fontes Geist do chat,
salvas em `src/app/fonts/`. Todas as fontes necessárias estão no repositório;
o build não precisa acessar Google Fonts nem Framer.

## Integração com o backend

Frontend e backend são dois processos separados. Preencher os envs não inicia
a API. Mantenha `uv run uvicorn app.main:app --reload` rodando na pasta `backend`
e `pnpm dev` na pasta `frontend`. Antes do primeiro uso, execute `uv sync --group dev`
e `uv run alembic upgrade head` no backend. O primeiro envio também baixa o modelo
de embeddings local; os seguintes reutilizam o cache.

Copie `.env.example` para `.env.local`. `BACKEND_API_URL` aponta para o FastAPI
(padrão `http://127.0.0.1:8000`), sem o sufixo `/api/v1`. Reinicie o Next após
alterar essa configuração. A variável é privada do servidor; nenhuma chave de IA
ou JWT deve ir para uma variável `NEXT_PUBLIC_*`.

O backend precisa estar configurado conforme `backend/.env.example`, com banco
migrado, `JWT_SECRET_KEY`, `GROQ_API_KEY` e documentos com embeddings para a busca.
As instruções de instalação, migração e ingestão estão no README da raiz.

O login é opcional e fica no header da landing e do chat. O botão **Entrar** abre
um diálogo independente da conversa. Em `/chat`, comece sem cadastro: a sessão
temporária permite 3 perguntas durante cerca de 4 horas, com quota controlada
pelo backend. Os temas preenchem o rascunho sem enviar automaticamente. O primeiro
envio cria a conversa e envia a pergunta. O histórico lateral permite retomar conversas e
carregar mais resultados. As respostas exibem as citações retornadas pela API;
expandir uma fonte consulta os metadados e o link oficial do trecho.

As chamadas passam por `/api/backend/*`, com endpoints e métodos permitidos
explicitamente. O JWT é guardado em cookie HttpOnly, SameSite=Lax e Secure em
produção, nunca em localStorage ou nas respostas de login enviadas ao cliente.
A sessão é validada pelo FastAPI. O token anônimo também fica em cookie HttpOnly;
o banco armazena apenas o hash. Ao entrar ou cadastrar, a API transfere as
conversas da sessão para a conta, preservando os IDs e as mensagens. Ao atingir
o limite, o chat mantém a conversa e indica o botão Entrar. Sair remove os cookies
e limpa os dados da conta na interface. O logout
é local: o backend atual não dispõe de revogação de tokens.

O envio não usa streaming porque o endpoint atual devolve uma resposta JSON
completa. Durante a espera, novos envios e trocas de conversa ficam bloqueados.
Em caso de falha, o chat consulta o histórico para recuperar a mensagem que o
backend pode já ter salvo; nunca repete o POST automaticamente. Se não conseguir
confirmar o estado, pede para atualizar a conversa antes de outro envio.

Para testar o contrato HTTP sem banco nem créditos de IA, após `pnpm build`:

```bash
pnpm test:integration
```

Esse teste inicia um Next de produção em porta livre e uma API de teste isolada.
Verifica sessão/cookie, autenticação, histórico, perguntas, citações, expiração,
falhas e restrições do gateway. Ele não substitui a validação ponta a ponta com
PostgreSQL, embeddings e Groq reais.

A decisão de acesso está registrada no [ADR 0006](../docs/adr/0006-login-opcional-e-conversa-anonima.md)
e nas seções 12 e 88 do overview. A atualização exige `uv run alembic upgrade head`
no backend para criar `anonymous_sessions` e o vínculo de propriedade da conversa.
