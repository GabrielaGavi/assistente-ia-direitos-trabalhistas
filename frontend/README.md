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

A rota `/` é renderizada por React/Next.js. As 11 seções da landing, navegação
e rodapé estão em `src/components/landing/`. A conversão preserva a estrutura,
as classes, as medidas e os breakpoints do visual aprovado. `landing.css`
contém os estilos e fontes; `styles.ts` reúne os estilos inline compartilhados.

Abas, carrossel, seletor de preços, menu e perguntas expansíveis usam estado
React. As mãos usam `landing-hands.tsx`, com Three.js importado do pacote:
mantêm a textura, o brilho e a animação rígida aprovados, sem hover.

Imagens, vídeos e fontes da landing estão em `public/assets/landing/`.
`asset-manifest.json` registra a origem de cada recurso apenas para referência.
O desenvolvimento e o build não leem HTML nem a pasta `specs/.../references`;
essa pasta pode ser removida sem afetar a aplicação. Não existe etapa de
geração da landing nem cópia de bibliotecas para `public/vendor`.

O layout compartilhado usa `next/font/local` com as mesmas fontes Geist do chat,
salvas em `src/app/fonts/`. Todas as fontes necessárias estão no repositório;
o build não precisa acessar Google Fonts nem Framer.

A rota `/chat` mantém a interface existente. Esta migração da landing não
implementa os endpoints de conversas previstos na especificação.
