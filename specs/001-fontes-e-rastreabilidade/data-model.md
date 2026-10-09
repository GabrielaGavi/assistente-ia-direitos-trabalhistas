# Data Model: Fontes Jurídicas e Rastreabilidade Documental

**Feature**: `001-fontes-e-rastreabilidade`  
**Date**: 2026-10-09

---

## 1. Diagrama de Relacionamentos

```text
┌───────────────────────────┐
│          Source           │
│───────────────────────────│
│ id: UUIDv7 (PK)           │
│ name: str                 │
│ short_name: str           │
│ base_url: str             │
│ description: str?         │
│ created_at: datetime      │
└─────────────┬─────────────┘
              │ 1
              │
              │ N
┌─────────────▼─────────────┐
│         Document          │
│───────────────────────────│
│ id: UUIDv7 (PK)           │
│ source_id: UUIDv7 (FK)    │
│ title: str                │
│ logical_name: str         │
│ version: int              │
│ checksum_sha256: str      │
│ published_at: datetime?   │
│ is_active: bool           │
│ status: DocumentStatus    │
│ created_at: datetime      │
│ updated_at: datetime      │
└─────────────┬─────────────┘
              │ 1
              │
              │ N
┌─────────────▼─────────────┐          ┌───────────────────────────┐
│       DocumentChunk       │          │         Citation          │
│───────────────────────────│          │───────────────────────────│
│ id: UUIDv7 (PK)           │ 1      N │ id: UUIDv7 (PK)           │
│ document_id: UUIDv7 (FK)  ├──────────┤ message_id: UUIDv7 (FK)   │
│ source_id: UUIDv7 (FK)    │          │ chunk_id: UUIDv7 (FK)     │
│ chunk_index: int          │          │ citation_number: int      │
│ content: str              │          │ original_quote: str       │
│ article: str?             │          │ created_at: datetime      │
│ section: str?             │          └───────────────────────────┘
│ paragraph: str?           │
│ page_number: int?         │
│ official_url: str         │
│ metadata_extra: JSONB?    │
│ created_at: datetime      │
└───────────────────────────┘
```

---

## 2. Entidades Detalhadas

### 2.1. `Source` (Fontes Oficiais)
Representa órgãos emissores de legislação ou repositórios oficiais.
- **Campos:**
  - `id`: UUID (Primary Key, gerado via UUID v7).
  - `name`: String(255), not null — Ex.: "Presidência da República - Portal da Legislação".
  - `short_name`: String(50), not null, unique — Ex.: "Planalto", "TST", "MTE".
  - `base_url`: String(500), not null — URL base da instituição (ex.: `https://www.planalto.gov.br`).
  - `description`: Text, nullable — Descrição institucional.
  - `created_at`: DateTime(timezone=True), default=UTC now.

### 2.2. `Document` (Normas e Leis)
Representa um documento jurídico versionado.
- **Campos:**
  - `id`: UUID (Primary Key, UUID v7).
  - `source_id`: UUID (Foreign Key $\rightarrow$ `Source.id`), not null.
  - `title`: String(255), not null — Ex.: "Consolidação das Leis do Trabalho (CLT)".
  - `logical_name`: String(100), not null — Identificador do documento (ex.: `clt-decreto-lei-5452-1943`).
  - `version`: Integer, not null, default=1.
  - `checksum_sha256`: String(64), not null — Hash SHA-256 do texto normalizado para validação de integridade e idempotência.
  - `published_at`: DateTime(timezone=True), nullable — Data oficial de publicação no Diário Oficial.
  - `is_active`: Boolean, not null, default=False — Indica se esta é a versão vigente para recuperação do RAG.
  - `status`: Enum(`PROCESSING`, `READY`, `FAILED`, `ACTIVE`, `INACTIVE`), not null, default=`PROCESSING`.
  - `created_at`: DateTime(timezone=True), default=UTC now.
  - `updated_at`: DateTime(timezone=True), default=UTC now.
- **Constraints:**
  - `uq_document_source_logical_version`: Unique(`source_id`, `logical_name`, `version`).
  - Regra de negócio (índice parcial): No máximo uma versão com `is_active = True` por `(source_id, logical_name)`.

### 2.3. `DocumentChunk` (Trechos Normativos Estruturados)
Unidade atômica com metadados jurídicos rastreáveis.
- **Campos:**
  - `id`: UUID (Primary Key, UUID v7).
  - `document_id`: UUID (Foreign Key $\rightarrow$ `Document.id`, on delete cascade), not null.
  - `source_id`: UUID (Foreign Key $\rightarrow$ `Source.id`), not null.
  - `chunk_index`: Integer, not null — Posição sequencial do trecho no documento.
  - `content`: Text, not null — Conteúdo original do trecho legal (não reescrito).
  - `article`: String(50), nullable — Ex.: "Art. 130".
  - `section`: String(100), nullable — Ex.: "Capítulo IV - Das Férias Anuais".
  - `paragraph`: String(50), nullable — Ex.: "§ 1º" ou "Inciso II".
  - `page_number`: Integer, nullable — Página no documento original (se PDF).
  - `official_url`: String(1000), not null — Link oficial direto para a norma no portal governamental.
  - `metadata_extra`: JSONB, nullable — Metadados estruturais adicionais.
  - `created_at`: DateTime(timezone=True), default=UTC now.
- **Constraints:**
  - `uq_chunk_document_index`: Unique(`document_id`, `chunk_index`).

### 2.4. `Citation` (Citações em Respostas)
Vínculo imutável entre a resposta do assistente e a evidência legal que a comprova.
- **Campos:**
  - `id`: UUID (Primary Key, UUID v7).
  - `message_id`: UUID, not null — ID da mensagem do assistente.
  - `chunk_id`: UUID (Foreign Key $\rightarrow$ `DocumentChunk.id`), not null.
  - `citation_number`: Integer, not null — Número da citação na resposta (`1`, `2`, `3`...).
  - `original_quote`: Text, not null — Trecho literal recuperado do chunk utilizado como evidência.
  - `created_at`: DateTime(timezone=True), default=UTC now.
- **Constraints:**
  - `uq_citation_message_number`: Unique(`message_id`, `citation_number`).

### 2.5. `AuditLog` (Trilha de Auditoria)
Registra ações administrativas na base jurídica.
- **Campos:**
  - `id`: UUID (Primary Key, UUID v7).
  - `action`: String(50), not null — `SOURCE_CREATED`, `DOCUMENT_UPLOADED`, `DOCUMENT_ACTIVATED`, `DOCUMENT_DEACTIVATED`, etc.
  - `entity_type`: String(50), not null — `Source`, `Document`.
  - `entity_id`: UUID, not null.
  - `actor_id`: UUID, nullable — Usuário administrador executor.
  - `details`: JSONB, nullable — Mudanças de estado anteriores e posteriores.
  - `created_at`: DateTime(timezone=True), default=UTC now.
