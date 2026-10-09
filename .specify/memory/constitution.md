# Constituição do Projeto: Assistente de Direitos Trabalhistas

## Princípios Fundamentais

### I. Desenvolvimento Orientado a Especificação (Spec-Kit)
- **Definir antes de construir:** Nenhuma funcionalidade deve ser implementada sem especificação clara (`/speckit-specify`), plano técnico estruturado (`/speckit-plan`) e decomposição em tarefas acionáveis (`/speckit-tasks`).
- **Critérios de aceitação verificáveis:** Toda tarefa deve conter critérios objetivos de validação e sucesso antes do início da codificação.
- **Rastreabilidade e alinhamento:** Mudanças de escopo e novas decisões técnicas devem ser refletidas nos artefatos de especificação.

### II. Priorização por Pareto (Foco em Valor e Mitigação de Riscos)
- **Construir primeiro o que sustenta o sistema:** Priorizar as funcionalidades centrais que geram 80% do valor e mitigam os maiores riscos técnicos e ético-jurídicos, e não as camadas meramente cosméticas.
  - **P0 (Crítico):** Fontes jurídicas e rastreabilidade, ingestão de documentos (PDF/OCR/URLs), busca híbrida (`pgvector` + `FTS` + `RRF` + Reranker) e geração com citações fundamentadas.
  - **P1 (Essencial):** Interface conversacional acessível, streaming via SSE, controle de quotas/sessão e observabilidade/avaliação de RAG.
  - **P2 (Diferencial):** Animações (GSAP/Lenis), microinterações e refinamentos estéticos visuais.
- **Pareto prioriza esforço, não dispensa testes:** A regra 80/20 orienta a ordem de desenvolvimento; testes de segurança, fidelidade documental e integridade das fontes continuam 100% obrigatórios.

### III. Test-Driven Development (TDD Obrigatório)
- **Ciclo Red-Green-Refactor estrito:**
  1. **RED:** Escrever o teste unitário/integração que falha, refletindo a especificação e o comportamento esperado.
  2. **GREEN:** Implementar a lógica mínima necessária para fazer o teste passar.
  3. **REFACTOR:** Refatorar o código visando manutenibilidade, desacoplamento e clareza, preservando o comportamento verificado.
- **Stack de testes oficial:** `pytest` no backend Python e ferramentas padronizadas no frontend (Playwright para E2E). Não importar bibliotecas de teste não acordadas (ex.: Vitest/Jest/Prisma).
- **Sem testes, sem conclusão:** Nenhuma tarefa é dada como concluída (`DONE`) apenas porque o código foi escrito. Ela deve satisfazer todos os critérios de aceitação e passar em todos os testes automatizados aplicáveis.

### IV. Groundedness Factual e Tolerância Zero a Alucinações Jurídicas
- **Evidência documental antes da resposta:** O modelo de linguagem (LLM) atua como sintetizador e tradutor de linguagem acessível, jamais como fonte primária de verdade jurídica.
- **Insuficiência de evidência explícita:** Se os chunks recuperados não contiverem evidências suficientes para responder à pergunta, o sistema retornará `INSUFFICIENT_EVIDENCE` e orientará o usuário para as fontes oficiais cadastradas. O assistente **nunca** inventará artigos, prazos, leis ou valores.
- **Citações rastreáveis:** Toda resposta afirmativa deve referenciar citações numéricas (`[1]`, `[2]`) diretamente associadas a `DocumentChunk` válidos e ativos no banco.
- **Isolamento de segurança:** Conteúdo de documentos é tratado como dado inerte, com proteção estrita contra *prompt injection*.

### V. Monólito Modular com Arquitetura Hexagonal (Ports and Adapters)
- **Domínios isolados:** Cada módulo do backend possui fronteiras bem delimitadas (auth, conversations, chat, rag, documents, ingestion, jobs).
- **Portas e Adaptadores:** Integrações externas (LLM Groq, Sentence-Transformers, Reranker, Object Storage, Neon PostgreSQL) devem se comunicar com o domínio exclusivamente através de interfaces abstratas (Ports), permitindo substituição sem afetar regras de negócio.

---

## Restrições e Padrões Tecnológicos

1. **Backend:** Python, FastAPI, Pydantic, SQLAlchemy 2 (Async), Alembic e pytest.
2. **Banco de Dados:** Neon PostgreSQL unificando persistência relacional, busca vetorial (`pgvector`) e busca textual (`Full Text Search`). Sem bancos vetoriais dedicados externos (sem Qdrant e sem ChromaDB no MVP).
3. **Frontend:** Next.js, TypeScript, Tailwind CSS, shadcn/ui, Zustand, TanStack Query, React Hook Form, Zod e Playwright.
4. **Comunicação:** API RESTful com JSON, OpenAPI 3.0 e streaming via SSE (Server-Sent Events).

---

## Fluxo de Trabalho (Development Workflow)

```
IDEIA / REQUISITO
       ↓
/speckit-specify (Problema, Escopo e Critérios de Aceitação)
       ↓
/speckit-plan (Plano Técnico, Decisões de Arquitetura e Contratos)
       ↓
/speckit-tasks (Decomposição em Tarefas Pequenas e Testáveis)
       ↓
PRIORIZAÇÃO PARETO (P0 → P1 → P2)
       ↓
TDD (RED → GREEN → REFACTOR)
       ↓
Testes de Regressão e Verificação de Critérios
       ↓
Auditoria e Conclusão (/speckit-converge)
```

---

## Governança do Projeto

- **Soberania da Constituição:** Esta constituição tem precedência sobre práticas informais. Qualquer alteração em princípios exige registro e justificativa.
- **Critério de Aceite Definitivo (Definition of Done):**
  1. Critérios de aceitação da especificação cumpridos.
  2. Testes automatizados escritos e passando (`pytest` / E2E).
  3. Conformidade estrita com a arquitetura hexagonal e ausência de acoplamento direto com providers.
  4. Nenhuma informação confidencial, credencial ou conteúdo sensível de mensagens exposto em logs.

**Versão**: 1.0.0 | **Ratificada**: 2026-10-09 | **Última Emenda**: 2026-10-09
