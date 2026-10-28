# Tasks: Fundação do Frontend

## Phase 1: Setup

- [x] T001 Criar a aplicação Next.js com TypeScript, App Router, Tailwind e pnpm em `frontend/`.
- [x] T002 Configurar metadados, idioma `pt-BR` e estilos globais em `frontend/src/app/layout.tsx` e `frontend/src/app/globals.css`.
- [x] T003 Registrar o sistema visual híbrido em `specs/002-frontend-foundation/visual-system.md`.

## Phase 2: Fundação visual

- [x] T004 Criar tokens de cor, espaçamento, superfícies, foco e motion em `frontend/src/app/globals.css`.
- [x] T005 Criar a landing responsiva baseada na composição do Optivio em `frontend/src/app/page.tsx` e `frontend/src/app/page.module.css`.
- [x] T006 Criar rota provisória de entrada do produto em `frontend/src/app/chat/page.tsx`.

## Phase 3: User Story 1 — Fazer uma pergunta com segurança (P1)

- [ ] T007 [US1] Consultar Context7 antes de adicionar componentes/bibliotecas de formulário, estado e streaming.
- [ ] T008 [US1] Criar componentes de conversa, composer e estados de mensagem em `frontend/src/features/chat/`.
- [ ] T009 [US1] Implementar parser SSE e cancelamento em `frontend/src/lib/api/` quando o contrato do backend estiver publicado.
- [ ] T010 [US1] Criar testes de componentes e E2E do fluxo de pergunta em `frontend/tests/`.

## Phase 4: User Story 2 — Conferir uma fonte citada (P1)

- [ ] T011 [US2] Criar cliente tipado para `GET /api/v1/citations/{id}` em `frontend/src/features/citations/api/`.
- [ ] T012 [US2] Criar popover/card de evidência literal em `frontend/src/features/citations/components/`.
- [ ] T013 [US2] Criar testes de contrato e acessibilidade para citações em `frontend/tests/`.

## Phase 5: Histórico, acesso e administração

- [ ] T014 [US3] Criar sidebar e operações de histórico em `frontend/src/features/conversations/` após contrato de conversas.
- [ ] T015 [US4] Criar área administrativa autorizada em `frontend/src/features/admin/` após contratos de fontes e documentos.

## Phase 6: Qualidade transversal

- [ ] T016 Validar teclado, contraste, `prefers-reduced-motion`, viewport de 320 px e build de produção em `frontend/`.
- [ ] T017 Definir o nome do agente e substituir a marca provisória em `frontend/src/app/` e metadados.
