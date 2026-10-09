# Implementation Plan: Fontes Jurídicas e Rastreabilidade Documental

**Branch**: `001-fontes-e-rastreabilidade` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-fontes-e-rastreabilidade/spec.md`

---

## Summary

Implementação do núcleo de domínio para gestão de **Fontes Jurídicas Oficiais** (`Source`), **Documentos Normativos Versionados** (`Document`), **Trechos Estruturados** (`DocumentChunk`) e **Citações Rastreáveis** (`Citation`), estabelecendo os alicerces de dados e integridade exigidos pelo RAG e pela Constituição do Projeto (Princípios I, II, III, IV e V).

---

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: FastAPI, Pydantic v2, SQLAlchemy 2 (Async), Alembic  
**Storage**: Neon PostgreSQL (PostgreSQL 16 com extensão `pgvector` e `uuid-ossp`)  
**Testing**: pytest, pytest-asyncio, httpx  
**Target Platform**: Linux / Render / Docker  
**Project Type**: Backend RESTful Web Service (Modular Monolith com Ports and Adapters)  
**Performance Goals**: Leitura de metadados de fontes e chunks em < 50ms p95  
**Constraints**: IDs gerados em formato UUID v7; datas em UTC; integridade transacional rigorosa; conformidade WCAG e OpenAPI 3.0  
**Scale/Scope**: ~10 fontes oficiais, centenas de normas legais consolidadas e milhares de chunks com metadados estruturados  

---

## Constitution Check

*GATE: Must pass before implementation. Re-check post-design.*

- [x] **Spec-Kit**: Especificação completa e critérios de aceite definidos em `spec.md`.
- [x] **Pareto P0**: Funcionalidade prioritária fundamental de sustentação do sistema.
- [x] **TDD Mandatório**: Planejamento estruturado em Red-Green-Refactor com `pytest`.
- [x] **Groundedness Factual**: Citações vinculadas a chunks oficiais; documentos inativos excluídos da busca.
- [x] **Arquitetura Hexagonal**: Casos de uso desacoplados de persistência por meio de repositories e schemas Pydantic.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-fontes-e-rastreabilidade/
├── spec.md              # Especificação de requisitos funcionais e critérios
├── plan.md              # Este plano de implementação técnica
├── research.md          # Pesquisa técnica e decisões de design
├── data-model.md        # Modelos relacionais e entidades
├── quickstart.md        # Guia de validação end-to-end
├── contracts/           # Contratos OpenAPI 3.0
│   └── sources-documents-api.yaml
└── checklists/
    └── requirements.md
```

### Source Code Layout (Backend)

```text
backend/
├── app/
│   ├── sources/
│   │   ├── models.py       # Modelo SQLAlchemy Source
│   │   ├── schemas.py      # Schemas Pydantic SourceCreate/Response
│   │   ├── repository.py   # Acesso ao banco assíncrono
│   │   ├── service.py      # Regras de negócio de fontes
│   │   └── router.py       # Endpoints /api/v1/sources
│   ├── documents/
│   │   ├── models.py       # Modelos Document e DocumentChunk
│   │   ├── schemas.py      # Schemas Pydantic DocumentCreate/ChunkResponse
│   │   ├── repository.py   # Repositório de documentos e chunks
│   │   ├── service.py      # Versionamento, checksum e ativação
│   │   └── router.py       # Endpoints /api/v1/documents
│   ├── citations/
│   │   ├── models.py       # Modelo Citation
│   │   ├── schemas.py      # Schemas de citação e detalhe
│   │   ├── repository.py   # Consulta e auditoria de citações
│   │   └── router.py       # Endpoints /api/v1/citations
│   └── shared/
│       ├── database.py     # Configuração SQLAlchemy async
│       ├── uuid.py         # Gerador de UUID v7
│       └── audit/          # Registro de AuditLog
└── tests/
    ├── unit/
    │   ├── test_sources.py
    │   ├── test_documents_versioning.py
    │   └── test_citations.py
    └── integration/
        └── test_sources_api.py
```
