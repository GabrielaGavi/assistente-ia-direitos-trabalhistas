# Tasks: Fontes Jurídicas e Rastreabilidade Documental

**Feature**: `001-fontes-e-rastreabilidade` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Estruturação inicial do backend e configuração de ferramentas

- [ ] T001 Criar estrutura de diretórios do backend modular em `backend/app` (`sources`, `documents`, `citations`, `shared`)
- [ ] T002 [P] Configurar `backend/pyproject.toml` com dependências (`fastapi`, `pydantic`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pytest`, `pytest-asyncio`, `httpx`)
- [ ] T003 [P] Configurar gerador de UUID v7 e utilitários de data UTC em `backend/app/shared/uuid.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura de persistência, conexão com o banco e suporte a testes

- [ ] T004 Implementar gerenciamento assíncrono de sessão do SQLAlchemy em `backend/app/shared/database.py`
- [ ] T005 [P] Implementar schemas base e modelo de auditoria em `backend/app/shared/audit/models.py`
- [ ] T006 [P] Configurar fixtures assíncronas do pytest para testes de banco em `backend/tests/conftest.py`
- [ ] T007 Configurar inicialização do Alembic e migrations em `backend/alembic/`

---

## Phase 3: User Story 1 - Rastreabilidade de Respostas e Auditoria de Citações (Priority: P1) 🎯 MVP

**Goal**: Garantir que citações numéricas `[1]` em respostas recuperem o trecho literal do `DocumentChunk` com metadados do artigo e link oficial governamental.

**Independent Test**: Criar citação associada a um chunk ativo e verificar que `GET /api/v1/citations/{id}` retorna o trecho literal íntegro, o artigo e a fonte oficial do Planalto.

### Tests for User Story 1 (TDD - RED) 🔴
- [ ] T008 [P] [US1] Escrever teste unitário para validação de schema de citação em `backend/tests/unit/test_citations_schema.py`
- [ ] T009 [P] [US1] Escrever teste de integração para o endpoint `GET /api/v1/citations/{id}` em `backend/tests/integration/test_citations_api.py`

### Implementation for User Story 1 (GREEN & REFACTOR) 🟢
- [ ] T010 [P] [US1] Implementar modelo SQLAlchemy `Citation` em `backend/app/citations/models.py`
- [ ] T011 [P] [US1] Implementar schemas Pydantic `CitationResponse` e `CitationDetailResponse` em `backend/app/citations/schemas.py`
- [ ] T012 [US1] Implementar repositório `CitationRepository` em `backend/app/citations/repository.py`
- [ ] T013 [US1] Implementar serviço `CitationService` com resolução de links em `backend/app/citations/service.py`
- [ ] T014 [US1] Implementar router FastAPI de citações em `backend/app/citations/router.py`

---

## Phase 4: User Story 2 - Cadastro e Versionamento de Normas Legais (Priority: P1)

**Goal**: Permitir o cadastro de fontes oficiais (`Source`) e documentos versionados (`Document`), garantindo no máximo uma versão ativa por norma lógica e prevenção de duplicidade por checksum.

**Independent Test**: Cadastrar fonte Planalto, criar documento CLT v1, verificar idempotência com mesmo checksum, criar v2 e certificar que ao ativar a v2 a v1 torna-se inativa.

### Tests for User Story 2 (TDD - RED) 🔴
- [ ] T015 [P] [US2] Escrever testes unitários de versionamento e unicidade de versão ativa em `backend/tests/unit/test_documents_versioning.py`
- [ ] T016 [P] [US2] Escrever testes de integração dos endpoints `POST /api/v1/sources` e `POST /api/v1/documents` em `backend/tests/integration/test_sources_documents_api.py`

### Implementation for User Story 2 (GREEN & REFACTOR) 🟢
- [ ] T017 [P] [US2] Implementar modelo SQLAlchemy `Source` em `backend/app/sources/models.py`
- [ ] T018 [P] [US2] Implementar modelo SQLAlchemy `Document` com enum de status em `backend/app/documents/models.py`
- [ ] T019 [P] [US2] Implementar schemas Pydantic para fontes (`SourceCreate`, `SourceResponse`) em `backend/app/sources/schemas.py`
- [ ] T020 [P] [US2] Implementar schemas Pydantic para documentos (`DocumentCreate`, `DocumentResponse`) em `backend/app/documents/schemas.py`
- [ ] T021 [US2] Implementar `SourceRepository` e `SourceService` em `backend/app/sources/repository.py` e `backend/app/sources/service.py`
- [ ] T022 [US2] Implementar `DocumentRepository` e `DocumentService` com lógica de transição de versão em `backend/app/documents/repository.py` e `backend/app/documents/service.py`
- [ ] T023 [US2] Implementar routers de fontes e documentos em `backend/app/sources/router.py` e `backend/app/documents/router.py`

---

## Phase 5: User Story 3 - Consulta e Filtragem de Trechos Oficiais (Priority: P2)

**Goal**: Permitir consultar e filtrar os trechos normativos (`DocumentChunk`) de um documento por artigo e seção com metadados completos.

**Independent Test**: Filtrar chunks por `article="Art. 130"` e validar a integridade dos campos estruturais e link oficial.

### Tests for User Story 3 (TDD - RED) 🔴
- [ ] T024 [P] [US3] Escrever testes unitários e de integração para filtragem de chunks em `backend/tests/unit/test_chunks_filter.py`

### Implementation for User Story 3 (GREEN & REFACTOR) 🟢
- [ ] T025 [P] [US3] Implementar modelo SQLAlchemy `DocumentChunk` em `backend/app/documents/chunk_models.py`
- [ ] T026 [P] [US3] Implementar schemas Pydantic para chunks (`DocumentChunkResponse`) em `backend/app/documents/chunk_schemas.py`
- [ ] T027 [US3] Implementar consulta estruturada de chunks no `DocumentRepository` em `backend/app/documents/repository.py`
- [ ] T028 [US3] Expor endpoint `GET /api/v1/documents/{id}/chunks` no router de documentos em `backend/app/documents/router.py`

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação final, validação cruzada e documentação OpenAPI

- [ ] T029 Integrar routers principais em `backend/app/main.py` com documentação automática OpenAPI (`/docs` e `/redoc`)
- [ ] T030 [P] Executar suíte completa de testes com `pytest` e gerar relatório de cobertura
- [ ] T031 Executar cenário de validação completo descrito em `specs/001-fontes-e-rastreabilidade/quickstart.md`
- [ ] T032 Executar `/speckit-analyze` para validação de consistência entre spec, plan e tasks

---

## Dependencies & Execution Order

```text
Phase 1: Setup (T001-T003)
   ↓
Phase 2: Foundational (T004-T007)
   ↓
Phase 3: US1 - Citações e Rastreabilidade (T008-T014) [MVP]
   ↓
Phase 4: US2 - Fontes e Versionamento (T015-T023)
   ↓
Phase 5: US3 - Filtragem de Trechos (T024-T028)
   ↓
Phase 6: Polish & Validação (T029-T032)
```
