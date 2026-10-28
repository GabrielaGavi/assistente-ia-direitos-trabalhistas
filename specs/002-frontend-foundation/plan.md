# Implementation Plan: Fundação do Frontend

**Branch**: `002-frontend-foundation` | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

## Summary

Criar o frontend como uma aplicação web independente dentro de `frontend/`, focada primeiro no chat com resposta rastreável. O App Router organiza rotas e layouts; componentes interativos ficam restritos às folhas de interação. O estado remoto fica nas consultas/mutações, enquanto o estado transitório de interface e streaming fica local ou em uma store pequena. O frontend consome somente contratos públicos REST e SSE; ele não recebe nem entende chunks, embeddings ou o pipeline RAG.

## Technical Context

**Language/Version**: TypeScript estrito; versão de Node LTS definida no bootstrap do frontend  
**Primary Dependencies**: Next.js App Router, React, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, React Hook Form, Zod e Playwright  
**Storage**: Não há banco local; dados persistentes pertencem ao backend. Preferências visuais podem usar persistência local não sensível.  
**Testing**: Testes de componentes e contratos de fronteira; Playwright para fluxos E2E  
**Target Platform**: Navegadores modernos em celular e desktop  
**Project Type**: Aplicação web em monorepo com backend independente  
**Performance Goals**: Primeira tela de chat utilizável em conexão móvel comum; feedback de envio imediato; 60 fps nas interações comuns; sem rolagem horizontal a 320 px  
**Constraints**: Mobile-first, WCAG como requisito de base, tema claro/escuro, respostas em Markdown sanitizado, nenhuma credencial ou token de refresh no browser, nenhum acoplamento com RAG  
**Scale/Scope**: MVP com chat, citações e histórico; autenticação e administração entram por fatias após os contratos correspondentes do backend

## Constitution Check

| Gate | Situação | Decisão |
|---|---|---|
| Spec-Kit antes da implementação | Aprovado | Esta especificação e este plano precedem tarefas e código. |
| Prioridade P0/P1 | Aprovado | Fontes/citações e chat precedem animações e efeitos visuais. |
| TDD e E2E | Aprovado | A próxima fase deverá começar pelos testes de componentes/contrato e cenários Playwright. |
| Groundedness | Aprovado | A UI expõe apenas citações públicas e evidencia insuficiência; não interpreta nem cria conteúdo jurídico. |
| Monólito modular/hexagonal | Aprovado | O frontend integra apenas a borda HTTP; clientes por domínio evitam que componentes conheçam detalhes do backend. |

## Architecture Decisions

1. **Next.js App Router como casca de rotas e composição.** Layouts e páginas permanecem no servidor por padrão. Componentes de chat, formulários, popovers de citação e provedores de estado são componentes cliente isolados. Isso mantém JavaScript enviado ao browser contido e impede acesso acidental a módulos privilegiados.
2. **Rotas por intenção e features por domínio.** Route groups separam a experiência pública, a área autenticada e a administrativa sem obrigar a URL a revelar a organização interna. Cada feature é dona de UI, esquema, tipos e cliente de API específicos.
3. **TanStack Query para estado remoto; Zustand somente para estado de interface compartilhado.** Listas de conversas, detalhes de citações e documentos são cache do servidor. Rascunho de mensagem, sidebar aberta e mensagem em streaming não são cache remoto e permanecem localmente, subindo para uma store apenas se compartilhados por telas/componentes distintos.
4. **SSE tratado como protocolo de domínio, não como renderização.** Um `fetch` com leitura de `ReadableStream` e parser SSE transforma eventos públicos (`status`, `text`, `sources`, `done`, `error`) em atualizações de uma mensagem temporária. Essa abordagem suporta o `POST` planejado e cabeçalho de autorização; `EventSource` nativo é restrito a GET. Apenas ao evento final a conversa e mensagens são invalidadas/refetchadas. Cancelar usa `AbortController` e o contrato de interrupção do backend quando existir.
5. **Citação carregada sob demanda.** A mensagem contém referências públicas. Ao abrir `[n]`, a interface consulta `GET /api/v1/citations/{id}`, renderiza o texto original sem reescrita e oferece o URL específico e a raiz institucional em nova aba segura.
6. **Segurança e acesso.** Token de acesso é mantido em memória; refresh é responsabilidade de cookie HttpOnly/backend. Se as telas autenticadas precisarem de SSR, o backend deverá oferecer uma sessão por cookie segura; um access token apenas em memória não pode ser usado pelo servidor do Next. Variáveis `NEXT_PUBLIC_*` carregam somente valores que podem ser públicos, como a URL pública da API; segredos permanecem no servidor. Markdown é permitido por allowlist, sem HTML arbitrário e links externos usam `rel="noopener noreferrer"`.

## Project Structure

### Documentation (this feature)

```text
specs/002-frontend-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── frontend-api-boundary.md
└── tasks.md                 # próxima fase; ainda não criado
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── (public)/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── (app)/
│   │   ├── chat/page.tsx
│   │   └── conversations/[conversationId]/page.tsx
│   ├── admin/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── api/                 # BFF apenas se necessário para sessão/ambiente
│   ├── layout.tsx
│   ├── providers.tsx
│   └── globals.css
├── components/
│   ├── ui/                  # componentes shadcn gerados
│   └── shared/              # cabeçalho, aviso legal, estados vazios/erro
├── features/
│   ├── chat/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── schemas/
│   │   └── types.ts
│   ├── citations/
│   ├── conversations/
│   ├── auth/
│   └── admin/
├── lib/
│   ├── api/                 # fetch, erros e parser SSE comuns
│   ├── markdown/
│   ├── formatters/
│   └── utils.ts
├── stores/
├── tests/
│   ├── component/
│   ├── contract/
│   └── e2e/
├── public/
└── .env.example
```

**Structure Decision**: `app/` trata composição e navegação; `features/` contém comportamento de produto; `components/` contém apenas elementos compartilhados. Não haverá pasta global genérica de “services” para evitar misturar domínios e contratos.

## Delivery Slices

| Ordem | Fatia | Dependência do backend | Resultado verificável |
|---|---|---|---|
| 1 | Fundação visual/acessibilidade | Nenhuma | Layout responsivo, tema, aviso legal e estados reutilizáveis. |
| 2 | Chat estático e renderer seguro | Nenhuma | Pergunta, mensagens, estados de resposta e Markdown seguro demonstráveis com fixtures. |
| 3 | Citação rastreável | `GET /api/v1/citations/{id}` já existe | Popover/card mostra trecho literal e links oficiais. |
| 4 | Conversas e streaming | Contratos ainda ausentes | Chat integrado, estados SSE, cancelar e histórico. |
| 5 | Sessão/autenticação | Contratos ainda ausentes | Sessão anônima, quota, login e migração de conversa. |
| 6 | Administração | Endpoints de fontes/documentos em conclusão | Listagem, estados e ações autorizadas. |
| 7 | Refinamento | Fatias anteriores | Animações opcionais, sem comprometer acessibilidade ou fluxo essencial. |

## Contract Gaps That Block Integration

- As rotas de conversa, mensagens, autenticação, quota, interrupção e administração aparecem no overview, mas ainda não estão registradas/expostas no backend atual.
- O contrato SSE precisa definir URL/método, cabeçalhos, evento inicial, payload de cada evento, status terminais e semântica de cancelamento.
- A resposta final de mensagem deve transportar referências públicas com `citation_id` e `citation_number`; texto contendo somente `[1]` não permite abrir a evidência de forma confiável.
- Devem ser padronizados CORS com origem explícita e credenciais, URL de ambiente e formato de erro. O formato conceitual atual é `error.code`, `error.message` e `error.details`, enquanto a rota de citação atual retorna o `detail` padrão do FastAPI.
- A rota atual de citações deve validar que a evidência pertence a uma conversa acessível à sessão solicitante; um UUID público não é autorização.

## Complexity Tracking

Nenhuma violação de princípio exige justificativa.
