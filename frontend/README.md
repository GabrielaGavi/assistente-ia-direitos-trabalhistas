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

A rota `/chat` é demonstrativa: não consulta fontes nem gera orientação jurídica.
Os endpoints de conversas previstos na especificação ainda precisam ser integrados.
