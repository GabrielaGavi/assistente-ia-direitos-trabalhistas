# RELATÓRIO TÉCNICO

## Arquitetura e Especificação do Sistema

**Projeto:** Assistente Inteligente de Orientação sobre Direitos Trabalhistas  
**Curso:** Ciência da Computação — FAESA  
**Tipo:** Projeto Integrador IV  
**Stack principal:** Next.js + TypeScript + FastAPI + Python + Neon PostgreSQL (pgvector + FTS) + Groq  
**Arquitetura:** Monólito Modular + Arquitetura Hexagonal (Ports and Adapters)  
**Versão:** 1.0 — Consolidada após entrevista arquitetural

---

# 1\. Visão geral

O projeto consiste em uma aplicação web capaz de auxiliar trabalhadores na compreensão de direitos trabalhistas por meio de perguntas em linguagem natural.

O sistema deverá utilizar **Retrieval-Augmented Generation (RAG)** para recuperar informações de uma base documental controlada e fornecer respostas fundamentadas em legislação e fontes oficiais.

O objetivo não é substituir advogados, sindicatos, órgãos públicos ou outros profissionais especializados. O sistema possui caráter **informativo e educacional**.

O relatório inicial define como temas principais férias, 13º salário, jornada de trabalho, horas extras, aviso-prévio, FGTS e rescisão contratual, além da exigência de recuperação de trechos relevantes, respostas acessíveis e apresentação das fontes utilizadas.

A metodologia também prevê preparação dos documentos para RAG, recuperação de trechos relevantes, integração entre frontend/backend/API de IA, testes e avaliação de qualidade, relevância, recuperação, alucinação e comportamento fora do escopo.

---

# 2\. Objetivo arquitetural

A arquitetura foi definida para atender simultaneamente:

- baixo acoplamento;
- facilidade de manutenção;
- separação de responsabilidades;
- segurança;
- rastreabilidade das respostas;
- possibilidade de evolução do RAG;
- processamento assíncrono de documentos;
- streaming das respostas;
- controle de uso;
- suporte a usuários anônimos e autenticados;
- administração da base de conhecimento;
- possibilidade de escalar o backend horizontalmente.

A solução não utilizará microservices no MVP.

A arquitetura será um **monólito modular combinado com arquitetura hexagonal (Ports and Adapters)**, permitindo separar claramente os domínios de negócio e isolar as regras centrais de tecnologias de infraestrutura e provedores externos sem introduzir a complexidade operacional de múltiplos serviços independentes.

---

# 3\. Arquitetura geral

``` text
┌─────────────────────────────────────────────────────────────┐
│                         USUÁRIO                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    NEXT.JS / TYPESCRIPT                      │
│                                                             │
│  Chat │ Histórico │ Auth │ Admin │ Documentos │ Citações   │
│                                                             │
│  Tailwind │ shadcn │ Zustand │ TanStack Query │ GSAP       │
│  Lenis │ Three.js │ React Hook Form │ Zod                   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTPS / SSE
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       FASTAPI                               │
│                     /api/v1                                 │
│                                                             │
│ ┌──────┐ ┌──────────────┐ ┌──────┐ ┌──────────────┐       │
│ │ Auth │ │Conversations │ │ Chat │ │  Documents   │       │
│ └──────┘ └──────────────┘ └───┬──┘ └──────┬───────┘       │
│                               │             │               │
│                         ┌─────▼─────┐ ┌────▼──────┐        │
│                         │    RAG    │ │ Ingestion │        │
│                         └─────┬─────┘ └────┬──────┘        │
│                               │             │               │
└───────────────────────────────┼─────────────┼───────────────┘
                                │             │
                    ┌───────────▼──────┐      │
                    │   PostgreSQL     │      │
                    │    + pgvector    │      │
                    └───────────┬──────┘      │
                                │             │
                    ┌───────────▼─────────────▼───┐
                    │           WORKER             │
                    │                              │
                    │ Jobs / OCR / Chunk / Embed   │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
                           Object Storage

External:
    ├── Groq — LLM
    ├── sentence-transformers — embeddings
    └── Reranker configurável
```

---

# 4\. Stack tecnológica

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zustand
- TanStack Query
- React Hook Form
- Zod
- GSAP
- Lenis
- Three.js
- Playwright

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2
- Alembic
- pytest

## Banco de Dados

- Neon PostgreSQL
- pgvector (busca vetorial)
- PostgreSQL Full Text Search (busca textual)

## Inteligência Artificial

- Groq
- Llama 3.3 70B
- sentence-transformers
- `paraphrase-multilingual-mpnet-base-v2`
- Reranker configurável

## Infraestrutura

- Docker
- Docker Compose
- Neon PostgreSQL gerenciado
- Object Storage S3-compatible
- Render
- GitHub Actions
- ambientes development, staging e production

---

# 5\. Arquitetura do backend

O backend adota o padrão de **Monólito Modular** com **Arquitetura Hexagonal (Ports and Adapters)**, organizado por **domínio** em vez de uma divisão global em camadas técnicas. O domínio e os casos de uso permanecem desacoplados de bibliotecas e recursos de infraestrutura externos.

Estrutura conceitual:

``` text
backend/
├── app/
│   ├── auth/
│   ├── users/
│   ├── conversations/
│   ├── chat/
│   ├── rag/
│   ├── documents/
│   ├── ingestion/
│   ├── jobs/
│   ├── sources/
│   └── shared/
│
├── tests/
├── alembic/
├── Dockerfile
└── pyproject.toml
```

Cada módulo poderá possuir internamente:

``` text
module/
├── router.py
├── service.py
├── repository.py
├── schemas.py
├── models.py
└── ...
```

### Responsabilidades

**Router**

Responsável apenas pela camada HTTP.

**Service**

Responsável pelas regras de negócio.

**Repository**

Responsável pelo acesso ao PostgreSQL.

**Schema**

Define contratos de entrada e saída da API.

**Model**

Representa entidades persistidas.

---

# 6\. Providers (Ports and Adapters)

Seguindo a arquitetura hexagonal, integrações externas e serviços de infraestrutura comunicam-se com o domínio exclusivamente através de **portas (interfaces abstratas)** e **adaptadores (implementações concretas)**.

Portas (Ports):

``` text
LLMProvider
EmbeddingProvider
Reranker
StorageProvider
```

Adaptadores iniciais (Adapters):

``` text
GroqLLMProvider
SentenceTransformerEmbeddingProvider
LocalReranker
S3StorageProvider
```

Isso permite substituir qualquer provedor externo ou tecnologia de infraestrutura sem alterar a lógica de negócio do domínio.

---

# 7\. Banco de dados

## Tecnologia

**Neon PostgreSQL + pgvector + Full Text Search (FTS)**.

O armazenamento relacional, a indexação vetorial (`pgvector`) e a busca textual (`FTS`) são unificados diretamente no **Neon PostgreSQL**. A arquitetura dispensa bancos vetoriais dedicados externos como **Qdrant** ou ChromaDB no MVP, reduzindo latência de rede, custo e complexidade operacional, além de assegurar integridade transacional ACID em uma única base de dados.

SQLAlchemy 2 será utilizado com abordagem assíncrona e Alembic para migrations.

IDs utilizarão **UUID v7**.

Datas serão armazenadas em **UTC**.

---

# 8\. Entidades principais

Modelo conceitual:

``` text
User
 │
 ├── AuthIdentity
 ├── RefreshSession
 ├── Conversation
 │      │
 │      └── Message
 │              │
 │              ├── AIExecution
 │              └── Citation
 │                       │
 │                       └── DocumentChunk
 │
 └── UsageDaily


Source
 │
 └── Document
        │
        └── DocumentChunk


AnonymousSession
 │
 └── Conversation


AuditLog
```

---

# 9\. User

A entidade `User` terá, conceitualmente:

``` text
id
email
password_hash
name
role
status
created_at
updated_at
deleted_at
```

Roles:

``` text
USER
ADMIN
```

O RBAC será centralizado no FastAPI.

O MVP não terá gerenciamento administrativo de usuários.

Administradores administrarão somente a base de conhecimento.

---

# 10\. AuthIdentity

A autenticação suportará:

- email + senha;
- Google OAuth/OIDC.

Para permitir múltiplos métodos de autenticação:

``` text
User 1:N AuthIdentity
```

Campos conceituais:

``` text
id
user_id
provider
provider_subject
created_at
```

Providers:

``` text
EMAIL_PASSWORD
GOOGLE
```

A associação de uma conta Google a uma conta existente exigirá confirmação adicional.

---

# 11\. Autenticação

Será utilizado:

``` text
Access Token
+
Refresh Token
```

Access token:

- duração aproximada: 15 minutos;
- mantido em memória no frontend.

Refresh token:

- duração aproximada: 30 dias;
- HttpOnly;
- persistência do hash no backend;
- associação com sessão/dispositivo;
- rotação a cada refresh.

O sistema terá:

``` text
refresh_sessions
```

com controle de:

- expiração;
- revogação;
- rotação;
- sessão/dispositivo.

---

# 12\. Usuário anônimo

Usuários não autenticados poderão utilizar o sistema.

Limite inicial:

``` text
3 perguntas
```

O limite será controlado pelo backend.

Será utilizada:

``` text
AnonymousSession
```

com:

``` text
id
token_hash
questions_used
questions_limit
reset_at
created_at
expires_at
```

O frontend armazenará apenas o identificador/token necessário.

IP será utilizado como mecanismo adicional de rate limiting, mas não como fonte única do controle de quota.

Após atingir o limite:

``` text
Usuário
   │
   ├── já autenticado → continua
   │
   └── anônimo
         ↓
      login
         ↓
      migração
         ↓
  conversa preservada
```

A conversa anônima será vinculada ao usuário através do preenchimento de `user_id` e remoção do vínculo com `anonymous_session_id`.

Não serão duplicadas mensagens.

Retenção inicial de sessão anônima: aproximadamente 4 horas.

---

# 13\. Conversações

Usuários autenticados poderão:

- criar conversas;
- possuir várias conversas;
- listar histórico;
- reabrir conversas;
- renomear;
- excluir;
- editar mensagens;
- interromper geração;
- regenerar respostas.

Estrutura conceitual:

``` text
Conversation
├── id
├── user_id
├── anonymous_session_id
├── title
├── created_at
├── updated_at
└── deleted_at
```

O título inicial será criado deterministicamente a partir da primeira pergunta, sem LLM.

O usuário poderá alterar o título.

Limite:

``` text
100 caracteres
```

O backend deverá sanitizar e validar o título.

---

# 14\. Mensagens

Uma única tabela:

``` text
messages
```

com separação entre:

``` text
role
status
```

Roles:

``` text
USER
ASSISTANT
SYSTEM
```

Statuses:

``` text
PENDING
PROCESSING
COMPLETED
INTERRUPTED
FAILED
OUT_OF_SCOPE
```

Um usuário pode editar sua mensagem existente.

A edição reutiliza a mesma linha da mensagem.

Não será criada uma segunda mensagem simplesmente por editar.

---

# 15\. Geração de resposta

Cada mensagem do usuário possui uma resposta associada.

A resposta não será duplicada em novas linhas quando ocorrer regeneração.

O sistema reutiliza a resposta/mensagem e cria novas tentativas de execução em:

``` text
AIExecution
```

Assim:

``` text
User Message
      │
      ▼
Assistant Message
      │
      ├── AIExecution #1 → FAILED
      ├── AIExecution #2 → INTERRUPTED
      └── AIExecution #3 → COMPLETED
```

A resposta parcial será preservada quando uma geração for interrompida.

---

# 16\. AIExecution

`AIExecution` representa uma tentativa concreta de geração.

Relacionamento:

``` text
AssistantMessage 1:N AIExecution
```

Dados armazenados:

``` text
model
embedding_model
retrieved_count
reranked_count
final_context_count
latency
status
reason
created_at
updated_at
```

Isso permite auditoria técnica e avaliação posterior do comportamento do RAG.

---

# 17\. Streaming

O streaming será feito através de **SSE (Server-Sent Events)**.

Fluxo:

``` text
POST /conversations/{id}/messages
              │
              ▼
           FastAPI
              │
              ▼
             RAG
              │
              ▼
             LLM
              │
              ▼
             SSE
              │
       ┌──────┼────────┐
       ▼      ▼        ▼
     status  text    sources
                       │
                       ▼
                      done
```

Eventos conceituais:

``` text
status
text
sources
done
error
```

Status exibidos ao usuário podem incluir:

``` text
Consultando fontes...
Elaborando resposta...
```

---

# 18\. API

A API é estruturada sob os padrões **RESTful**, com payload em formato **JSON**, documentação automática via **OpenAPI (Swagger)** e suporte nativo a **SSE (Server-Sent Events)** para streaming de respostas.

Padrões adotados:

- **Estilo:** RESTful
- **Prefixo:** `/api/v1`
- **Formato:** JSON
- **Documentação:** OpenAPI 3.0 (Swagger UI em `/docs` e ReDoc em `/redoc`)
- **Streaming:** SSE (Server-Sent Events) via HTTP

Erros padronizados:

``` json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensagem",
    "details": {}
  }
}
```

---

# 19\. Endpoints principais

## Health

``` http
GET /api/v1/health
```

## Conversações

``` http
POST /api/v1/conversations

GET /api/v1/conversations

GET /api/v1/conversations/{conversation_id}

PATCH /api/v1/conversations/{conversation_id}

DELETE /api/v1/conversations/{conversation_id}
```

## Mensagens

``` http
GET /api/v1/conversations/{conversation_id}/messages

POST /api/v1/conversations/{conversation_id}/messages
```

## Administração

``` http
POST /api/v1/admin/knowledge-base/documents

POST /api/v1/admin/knowledge-base/urls

POST /api/v1/admin/documents/{id}/reprocess

PATCH /api/v1/admin/documents/{id}
```

---

# 20\. Paginação

Será utilizada:

``` text
offset
limit
```

Exemplo conceitual:

``` text
GET /conversations?offset=0&limit=20
```

---

# 21\. Contrato do chat

Request:

``` json
{
  "message": "Quantos dias de férias eu tenho?"
}
```

Response/stream final deverá disponibilizar:

``` text
message
status
citations
usage
```

O frontend não terá conhecimento de:

- embeddings;
- pgvector;
- chunks;
- reranking;
- Groq;
- pipeline interno.

Isso fica exclusivamente no backend.

---

# 22\. Citações

As respostas utilizarão:

``` text
[1]
[2]
[3]
```

As referências serão clicáveis.

Exemplo:

``` text
O trabalhador possui direito a férias após o período
aquisitivo [1].
```

O frontend poderá abrir um card/popover contendo:

``` text
Título
Organização
Trecho original
Seção
Artigo
Parágrafo
Página
Link específico
Link oficial
```

Campos específicos são opcionais.

---

# 23\. Regra de citações

O LLM recebe identificadores internos dos chunks.

Exemplo:

``` text
[chunk_abc123]
```

O LLM pode produzir:

``` text
... conforme [chunk_abc123].
```

O backend:

1. valida o identificador;
2. confirma que ele pertence ao contexto fornecido;
3. transforma em `[1]`;
4. associa ao `DocumentChunk`;
5. persiste a `Citation`.

O frontend nunca recebe os IDs internos dos chunks como mecanismo de citação.

A numeração segue a **primeira aparição na resposta**.

Cada chunk utilizado possui uma Citation individual, mesmo quando múltiplos chunks pertencem ao mesmo documento.

---

# 24\. Documentos

Modelo:

``` text
Source 1:N Document 1:N DocumentChunk
```

Uma `Source` representa a fonte lógica/oficial.

Exemplo:

``` text
Source
└── Planalto

Document
└── CLT — versão X

DocumentChunk
├── Art. ...
├── Art. ...
└── Art. ...
```

Cada documento possui uma Source primária.

---

# 25\. Versionamento

Cada versão do documento será preservada.

Campos:

``` text
version
checksum
published_at
is_active
status
```

Somente uma versão poderá estar ativa para determinada fonte/documento lógico.

Fluxo:

``` text
Versão antiga
      │
      ▼
  INACTIVE

Nova versão
      │
      ▼
 PROCESSING
      │
      ▼
   READY
      │
      ▼
 revisão admin
      │
      ▼
    ACTIVE
```

A versão antiga permanece armazenada.

Alterações de conteúdo criam nova versão.

Correções somente de metadata não exigem nova versão.

---

# 26\. Status de documento

Estados:

``` text
PROCESSING
READY
FAILED
```

Somente:

``` text
READY + ACTIVE
```

pode entrar no RAG.

Documentos inativos jamais serão utilizados como fallback de conhecimento.

---

# 27\. Administração da base de conhecimento

Somente `ADMIN` poderá:

- enviar PDF;
- adicionar URL oficial;
- cadastrar documento;
- editar metadata;
- ativar;
- desativar;
- reprocessar;
- substituir versão;
- excluir logicamente.

Não haverá gerenciamento administrativo de usuários no MVP.

---

# 28\. Object Storage

Arquivos originais não serão armazenados diretamente no PostgreSQL.

Arquitetura:

``` text
PostgreSQL
→ metadata

Object Storage
→ PDF / arquivos originais
```

Storage:

``` text
S3-compatible
```

Provider configurável por ambiente.

---

# 29\. Ingestion

Entradas:

- PDF;
- URL oficial;
- Markdown.

Formato interno canônico:

``` text
Markdown
```

Pipeline:

``` text
Input
 │
 ├── PDF ──→ Extração de texto
 │              │
 │              └── baixa qualidade → OCR
 │
 ├── URL ──→ Fetch
 │             ↓
 │          HTML
 │             ↓
 │       extração principal
 │             ↓
 │          Markdown
 │
 └── Markdown ──→ normalização
                       │
                       ▼
                  Chunking
                       │
                       ▼
                  Embedding
                       │
                       ▼
                  PostgreSQL
```

---

# 30\. PDF e OCR

Primeiro:

``` text
extração normal
```

Depois:

``` text
quality measure
```

Se a qualidade for insuficiente:

``` text
OCR
```

Tecnologia inicial:

``` text
Tesseract
```

O documento registra o método:

``` text
TEXT
OCR
```

Mesmo documentos processados por OCR poderão atingir `READY`.

---

# 31\. URL ingestion

O worker/backend realizará o fetch.

O sistema deverá:

- seguir redirects;
- registrar a URL final;
- preservar a URL original;
- extrair `main/article` quando disponível;
- utilizar fallback para `body`;
- normalizar para Markdown.

Checksum será calculado após normalização.

Se o conteúdo não mudou:

``` text
não criar nova versão
```

Atualizações de URL serão manuais pelo administrador.

---

# 32\. Chunking

Chunking será:

- estrutural;
- semântico;
- consciente de artigos/seções;
- com overlap configurável.

Grandes artigos poderão ser divididos em subchunks.

O metadata do artigo original será preservado.

Metadata mínimo:

``` text
document_id
source_id
title
organization
url
page
section
article
paragraph
chunk_index
```

---

# 33\. Embeddings

Modelo inicial:

``` text
sentence-transformers/
paraphrase-multilingual-mpnet-base-v2
```

Embedding armazenado diretamente em:

``` text
document_chunks.embedding
```

Vetores serão consultados via pgvector.

Distância:

``` text
cosine similarity
```

---

# 34\. Busca híbrida

O RAG utilizará duas estratégias.

### Busca semântica

``` text
pgvector
→ 20 candidatos
```

### Busca textual

``` text
PostgreSQL FTS
→ 20 candidatos
```

As listas serão combinadas através de:

``` text
RRF
Reciprocal Rank Fusion
```

---

# 35\. Reranking

Depois do RRF:

``` text
20 candidatos
      ↓
   Reranker
      ↓
20 candidatos reranqueados
```

O reranker será configurável.

A implementação inicial será local.

Existe uma abstração:

``` text
Reranker
```

permitindo troca futura do modelo.

---

# 36\. Seleção de contexto

O contexto final do LLM não terá tamanho fixo.

Será calculado dinamicamente conforme:

- limite de tokens;
- tamanho da conversa;
- tamanho dos chunks;
- evidências disponíveis.

Fluxo:

``` text
20 + 20
   ↓
RRF
   ↓
20
   ↓
Reranker
   ↓
20
   ↓
Threshold + minimum evidence
   ↓
Contexto final dinâmico
```

---

# 37\. Threshold e evidência mínima

O sistema não utilizará apenas o primeiro resultado.

Haverá:

- threshold configurável;
- quantidade mínima de evidências.

Se a recuperação não atingir o nível necessário:

``` text
não responder com conhecimento inventado
```

---

# 38\. Escopo

Antes do RAG será realizada uma verificação de escopo.

Fluxo:

``` text
Pergunta
   ↓
Scope classifier
   ↓
┌───────────────┬────────────────┐
│ dentro escopo│ fora do escopo │
│       ↓       │       ↓        │
│      RAG      │ resposta curta │
└───────────────┴────────────────┘
```

Classificação:

``` text
regras
+
classificador pequeno/LLM barato
```

Perguntas fora do escopo não consomem quota.

---

# 39\. Proteção contra prompt injection

Os chunks recuperados serão tratados como **dados**, e não como instruções.

Haverá:

- delimitação clara da evidência;
- proteção contra prompt injection;
- isolamento dos chunks;
- instruções do sistema separadas do conteúdo recuperado.

O LLM não poderá alterar as regras do sistema através do conteúdo documental.

---

# 40\. Contexto da conversa

O histórico não será enviado integralmente indefinidamente.

Será utilizado:

``` text
contexto dinâmico por tokens
```

A prioridade será dada às informações mais relevantes para a pergunta atual.

O contexto RAG será inserido em uma seção claramente delimitada.

---

# 41\. Política do LLM

O modelo deverá:

- responder em linguagem acessível;
- utilizar evidências recuperadas;
- priorizar fontes oficiais;
- não inventar artigos;
- não inventar leis;
- não inventar prazos;
- não inventar valores;
- não utilizar conhecimento jurídico próprio como evidência.

Afirmações jurídicas factuais precisam estar fundamentadas.

Transições triviais da linguagem não precisam de citação.

---

# 42\. Conflito entre fontes

Prioridade:

``` text
Fonte oficial atual/vigente
        ↓
Fonte oficial secundária
        ↓
Fonte anterior/relevância menor
```

Fontes desatualizadas não serão utilizadas se existir evidência atual adequada.

Quando houver conflito que não possa ser resolvido automaticamente:

- o sistema prioriza fonte vigente;
- o LLM poderá sinalizar a existência do conflito;
- nunca deverá inventar uma resolução.

---

# 43\. Insuficiência de evidência

Esta é uma regra central do sistema.

Se o RAG não encontrar evidência suficiente:

``` text
NÃO:
"provavelmente a lei diz..."
```

O sistema deverá informar que não encontrou evidência suficiente.

Além disso, poderá fornecer orientação para fontes confiáveis relacionadas.

Essas fontes vêm do banco:

``` text
registered sources
```

Nunca serão URLs inventadas pelo LLM.

Contrato conceitual:

``` json
{
  "status": "INSUFFICIENT_EVIDENCE",
  "message": "...",
  "guidance": {
    "sources": []
  },
  "citations": []
}
```

---

# 44\. Quotas

Usuários autenticados possuem limite diário configurável.

O limite não ficará hardcoded.

Configuração:

``` text
.env
+
database
```

Para controle diário:

``` text
UsageDaily
```

A quota será consumida quando:

- a pergunta for válida;
- estiver dentro do escopo;
- o processamento tiver começado.

Não consome quota quando:

- pergunta vazia/inválida;
- fora do escopo;
- erro interno antes do processamento;
- falha do provider antes do processamento.

Se o streaming quebrar depois do processamento começar:

``` text
quota consumida
```

---

# 45\. Configuração

Parâmetros relevantes serão configuráveis.

Arquitetura:

``` text
Environment variables
        +
Database configuration
```

Isso permite alterar sem recompilar:

- quotas;
- modelos;
- thresholds;
- número de candidatos;
- parâmetros de RAG;
- limites;
- URLs;
- credenciais;
- configurações de providers.

---

# 46\. Concorrência

O frontend desabilitará envio concorrente na mesma conversa.

O backend também protegerá contra múltiplas gerações simultâneas.

Fluxo:

``` text
Conversation
     │
     └── geração ativa
             │
             └── novo request → bloqueado
```

---

# 47\. Interrupção

O usuário poderá interromper a geração.

A resposta parcial será preservada:

``` text
AssistantMessage
status = INTERRUPTED
content = partial content
```

A mensagem poderá posteriormente ser regenerada.

---

# 48\. Regeneração

Regenerar não cria uma nova assistant message.

É criada uma nova tentativa:

``` text
AssistantMessage
│
├── AIExecution #1
└── AIExecution #2
```

Isso mantém a conversa semanticamente limpa e permite rastrear tentativas.

---

# 49\. Exclusão de conversa

Será utilizado:

``` text
soft delete
```

com:

``` text
deleted_at
```

Posteriormente:

``` text
hard delete
```

Após a exclusão definitiva, mensagens, citações e execuções relacionadas poderão ser removidas em cascade.

---

# 50\. Usuário e privacidade

O usuário poderá solicitar exclusão da conta.

O processo deverá:

- remover ou anonimizar dados pessoais conforme retenção;
- aplicar política de retenção;
- preservar somente aquilo que for necessário legalmente/técnicamente.

Dados sensíveis de conversas não devem aparecer nos logs técnicos.

---

# 51\. AuditLog

A aplicação terá auditoria persistente.

O `AuditLog` registrará ações administrativas relevantes.

Não deverá registrar conteúdo integral de perguntas e respostas.

Exemplos:

``` text
DOCUMENT_UPLOADED
DOCUMENT_ACTIVATED
DOCUMENT_DEACTIVATED
DOCUMENT_REPROCESSED
DOCUMENT_UPDATED
```

---

# 52\. Segurança

Medidas definidas:

- bcrypt;
- JWT access token;
- refresh token rotativo;
- refresh token armazenado via HttpOnly;
- hash de refresh tokens no banco;
- RBAC;
- CORS com origens configuradas;
- rate limit por IP + usuário;
- rate limit configurável por endpoint;
- proteção contra prompt injection;
- validação Pydantic;
- sanitização de Markdown;
- não registrar conteúdo das mensagens em logs técnicos.

---

# 53\. Rate limiting

Será aplicado:

``` text
IP
+
User
```

e configurado por endpoint.

Exemplos conceituais:

``` text
/login
/chat
/admin/*
/documents/*
```

poderão possuir limites diferentes.

---

# 54\. Frontend

Estrutura conceitual:

``` text
frontend/
├── app/
│   ├── page
│   ├── chat/
│   ├── login/
│   ├── conversations/
│   └── admin/
│
├── components/
├── features/
│   ├── chat/
│   ├── auth/
│   ├── conversations/
│   └── admin/
│
├── lib/
├── hooks/
├── stores/
└── schemas/
```

A divisão exata de diretórios poderá ser refinada durante implementação sem alterar os contratos.

---

# 55\. Gerenciamento de estado

Estado global:

``` text
Zustand
```

Server state:

``` text
TanStack Query
```

Estado local permanecerá nos componentes quando não houver necessidade de compartilhamento.

---

# 56\. Formulários

``` text
React Hook Form
+
Zod
```

Zod será utilizado tanto para validação quanto para manter contratos explícitos no frontend.

---

# 57\. UI

Design system:

``` text
shadcn/ui
+
Tailwind CSS
```

Responsividade:

``` text
Mobile-first
+
Desktop completo
```

Não será desenvolvido apenas para mobile.

---

# 58\. Tema

A aplicação suportará:

``` text
Light
Dark
```

---

# 59\. Acessibilidade

Acessibilidade será requisito desde o início.

Objetivo:

``` text
WCAG
```

Isso inclui atenção a:

- contraste;
- teclado;
- foco;
- semântica;
- leitores de tela;
- estados de erro;
- labels;
- navegação.

---

# 60\. Chat UX

O chat deverá possuir:

- mensagens do usuário;
- resposta da IA;
- streaming;
- botão parar;
- Markdown;
- citações;
- cards de fontes;
- estados de carregamento;
- erros específicos;
- regeneração;
- edição de mensagem;
- histórico.

---

# 61\. Markdown

As respostas serão renderizadas como:

``` text
Markdown sanitizado
```

Nunca será permitido simplesmente renderizar HTML arbitrário proveniente do LLM.

---

# 62\. Citações na interface

Formato:

``` text
A legislação estabelece determinado direito [1].
```

O usuário poderá clicar:

``` text
[1]
 ↓
┌───────────────────────────────┐
│ CLT                           │
│ Planalto                      │
│                               │
│ "Trecho original..."          │
│                               │
│ Art. XXX                      │
│ Página XX                     │
│                               │
│ Ver fonte específica          │
│ Ver fonte oficial             │
└───────────────────────────────┘
```

O trecho apresentado deve ser o **trecho original do chunk**.

O frontend pode truncá-lo visualmente e permitir expansão.

Não deve reescrever o trecho.

---

# 63\. Histórico

Será apresentado através de uma sidebar/lista de conversas.

Operações:

``` text
Nova conversa
Abrir conversa
Renomear
Excluir
```

No MVP não haverá busca semântica/textual dentro do histórico.

---

# 64\. Área administrativa

Rota:

``` text
/admin
```

Funcionalidades:

``` text
Documentos
Fontes
Upload
URL
Processamento
Ativação
Desativação
Reprocessamento
Versionamento
```

Status visuais:

``` text
PROCESSING
READY
FAILED
ACTIVE
INACTIVE
```

---

# 65\. Upload

A interface administrativa terá:

- drag \& drop;
- seletor de arquivo;
- indicação de progresso/status;
- informações do documento;
- resultado do processamento.

---

# 66\. Processamento assíncrono

O upload não deverá ficar bloqueado esperando OCR, chunking e embeddings.

Fluxo:

``` text
Admin
 │
 ▼
POST upload
 │
 ▼
Document PROCESSING
 │
 ▼
Job criado
 │
 ▼
Worker
 │
 ├── extraction
 ├── OCR
 ├── normalization
 ├── metadata
 ├── chunking
 ├── embedding
 └── persist
 │
 ▼
READY
 │
 ▼
Admin review
 │
 ▼
ACTIVE
```

---

# 67\. Job Queue

Não será utilizado Redis no MVP.

A fila será persistida no PostgreSQL.

Worker executará jobs através de mecanismo de claim atômico.

Conceito:

``` text
jobs
├── PENDING
├── PROCESSING
├── COMPLETED
└── FAILED
```

Claim utilizando transação/lock.

---

# 68\. Retry

Jobs terão:

``` text
3 retries
```

com backoff.

Após falhas:

``` text
FAILED
```

e registro de:

``` text
error_code
error_message
timestamp
```

Jobs presos poderão ser recuperados através de:

``` text
locked_at
+
timeout
```

Outro worker poderá assumir o job.

---

# 69\. Worker

O worker utiliza o mesmo código-base do backend, mas roda como processo separado.

``` text
FastAPI process
       +
Worker process
```

Não é microservice independente.

---

# 70\. Infraestrutura local

Docker Compose:

``` text
docker-compose.yml

services:
  postgres
  backend
  worker
```

O frontend Next.js ficará fora do Docker durante desenvolvimento.

---

# 71\. Produção

Arquitetura escolhida:

``` text
Vercel/Render
```

Conforme decisão consolidada:

``` text
Frontend → Render
Backend  → Render
Worker   → Render
Database → PostgreSQL gerenciado
Storage  → S3-compatible
```

A arquitetura mantém o backend stateless.

---

# 72\. Ambientes

Serão considerados:

``` text
development
staging
production
```

Fluxo:

``` text
feature/*
    ↓
develop
    ↓
staging
    ↓
main
    ↓
production
```

`main` será protegida.

---

# 73\. CI/CD

GitHub Actions:

``` text
push / PR
   ↓
lint
   ↓
tests
   ↓
build
   ↓
deploy
```

Deploy será automatizado conforme o ambiente.

---

# 74\. Secrets

Desenvolvimento:

``` text
.env
```

Produção:

``` text
Provider Secrets
```

Nenhuma credencial deverá ser versionada.

---

# 75\. Migrations

Alembic será utilizado.

As migrations serão executadas explicitamente no processo de deploy/infraestrutura, e não como comportamento automático do startup da aplicação.

---

# 76\. Seed

Dados iniciais serão inseridos por processo explícito.

Não haverá seed automático em cada startup.

---

# 77\. Ingestion inicial

A carga inicial da base de conhecimento será realizada como processo separado.

O backend não executará ingestion automaticamente ao iniciar.

---

# 78\. Backup

PostgreSQL gerenciado deverá utilizar backup automático.

---

# 79\. Logs e observabilidade

Logs:

``` text
estruturados
```

Não deverão conter conteúdo das mensagens.

Health check deverá considerar:

- aplicação;
- banco;
- worker/jobs.

Error tracking externo será configurável.

---

# 80\. Escalabilidade

Backend stateless:

``` text
             ┌── Backend #1
Load Balancer┼── Backend #2
             └── Backend #N
                    │
                    ▼
               PostgreSQL
```

Estado não deve ficar armazenado na memória do processo.

Sessões, conversas, quotas e jobs ficam persistidos.

---

# 81\. Cache

Não será utilizado Redis no MVP.

Quando necessário:

- cache HTTP;
- PostgreSQL;
- mecanismos internos apropriados.

Redis poderá ser introduzido posteriormente caso exista necessidade comprovada.

---

# 82\. Testes

Backend:

``` text
Unit
Integration
API
```

Frontend:

``` text
Unit/component
E2E
```

E2E:

``` text
Playwright
```

---

# 83\. Testes de RAG

Será criado um dataset fixo de avaliação contendo:

``` text
Pergunta
Expected scope
Expected sources
Expected evidence
Expected behavior
```

Métricas/avaliações:

- qualidade;
- relevância;
- recuperação;
- groundedness;
- hallucination;
- comportamento fora do escopo.

Isso está alinhado à metodologia prevista no relatório inicial do projeto.

---

# 84\. Fluxo completo de uma pergunta

``` text
Usuário
   │
   ▼
Frontend
   │
   ▼
POST /conversations/{id}/messages
   │
   ▼
Autenticação / AnonymousSession
   │
   ▼
Validação
   │
   ▼
Quota
   │
   ▼
Scope Classifier
   │
   ├── OUT_OF_SCOPE
   │       ↓
   │    resposta
   │
   └── IN_SCOPE
           ↓
        Hybrid Search
           │
           ├── pgvector → 20
           └── FTS      → 20
                    ↓
                   RRF
                    ↓
                 20
                    ↓
                Reranker
                    ↓
           threshold/evidence
                    ↓
          contexto dinâmico
                    ↓
                  LLM
                    ↓
             valida citations
                    ↓
              persiste resposta
                    ↓
                   SSE
                    ↓
                Frontend
```

---

# 85\. Fluxo de insuficiência de evidência

``` text
Pergunta
   ↓
RAG
   ↓
Evidência insuficiente
   ↓
NÃO inventar resposta
   ↓
INSUFFICIENT_EVIDENCE
   ↓
Mensagem explicativa
   ↓
Fontes relacionadas registradas
   ↓
Frontend apresenta links
```

---

# 86\. Fluxo de documento

``` text
Admin
  ↓
Upload/URL
  ↓
Document PROCESSING
  ↓
Job
  ↓
Worker
  ↓
Extração
  ↓
OCR se necessário
  ↓
Markdown
  ↓
Metadata
  ↓
Chunking
  ↓
Embedding
  ↓
READY
  ↓
Admin Review
  ↓
ACTIVE
  ↓
Disponível no RAG
```

---

# 87\. Fluxo de atualização de documento

``` text
Documento ativo v1
       ↓
Admin atualiza
       ↓
checksum
       │
       ├── igual → nenhuma nova versão
       │
       └── diferente
              ↓
          Documento v2
              ↓
          PROCESSING
              ↓
            READY
              ↓
        revisão administrativa
              ↓
            ACTIVE
              ↓
          v1 INACTIVE
```

---

# 88\. Fluxo de autenticação anônima

``` text
Usuário anônimo
      ↓
AnonymousSession
      ↓
Perguntas 1–3
      ↓
Limite atingido
      ↓
Login
      ↓
User criado/autenticado
      ↓
Conversation.user_id = User.id
      ↓
anonymous_session_id = NULL
      ↓
Histórico preservado
```

---

# 89\. Fluxo de regeneração

``` text
Assistant Message
      │
      ├── Execution #1
      │
      ▼
Regenerate
      │
      ▼
Nova AIExecution
      │
      ▼
Novo resultado
      │
      ▼
Mesma Assistant Message
```

---

# 90\. Fluxo de edição

``` text
User Message
      ↓
Edit
      ↓
mesmo Message.id
      ↓
novo conteúdo
      ↓
reprocessamento
      ↓
Assistant response atualizada
```

---

# 91\. Fluxo de exclusão

``` text
DELETE Conversation
        ↓
deleted_at
        ↓
não aparece mais no histórico
        ↓
retenção
        ↓
hard delete
        ↓
cascade
```

---

# 92\. Estrutura de alto nível do projeto

``` text
project/
│
├── frontend/
│   ├── Next.js
│   ├── TypeScript
│   ├── Tailwind
│   ├── shadcn
│   ├── Zustand
│   ├── TanStack Query
│   ├── GSAP
│   ├── Lenis
│   └── Three.js
│
├── backend/
│   ├── FastAPI
│   ├── auth
│   ├── users
│   ├── conversations
│   ├── chat
│   ├── rag
│   ├── documents
│   ├── ingestion
│   ├── jobs
│   └── sources
│
├── worker/
│   └── processamento assíncrono
│
├── infrastructure/
│   ├── docker
│   └── deployment
│
├── tests/
│   ├── backend
│   ├── frontend
│   ├── integration
│   └── rag-evaluation
│
└── docs/
    ├── architecture
    ├── api
    ├── rag
    └── deployment
```

---

# 93\. Ferramentas de desenvolvimento assistido

Foram definidas como ferramentas complementares:

### Context7 MCP

Utilizado para consultar documentação atualizada das bibliotecas durante o desenvolvimento assistido por IA.

### Spec-Kit

Utilizado como kit de ferramentas para Desenvolvimento Dirigido por Especificações (Spec-Driven Development), estabelecendo constituição, especificações, planos e tarefas antes da implementação (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, `/speckit-converge`).

### Impeccable

Utilizado como apoio à qualidade visual e refinamento da interface.

### GSAP

Responsável por animações complexas.

### Lenis

Responsável pela experiência de scroll suave.

### Three.js

Disponível para experiências 3D específicas que agreguem valor à interface.

Three.js não deverá ser utilizado indiscriminadamente em toda a aplicação.

---

# 94\. Princípios arquiteturais

O projeto seguirá estes princípios:

### 1\. Backend como fonte de verdade

Quotas, autorização, ownership e regras críticas não dependem do frontend.

### 2\. RAG como fonte factual

O LLM não é considerado fonte jurídica.

### 3\. Evidência antes de resposta

Sem evidência suficiente, o sistema não inventa.

### 4\. Fontes rastreáveis

Toda citação deve apontar para um `DocumentChunk`.

### 5\. Dados persistentes

Estado importante não fica somente em memória.

### 6\. Providers desacoplados

LLM, embeddings, reranker e storage podem ser substituídos.

### 7\. Processamento assíncrono

Documentos não bloqueiam requests HTTP.

### 8\. Versionamento

Documentos antigos não são sobrescritos.

### 9\. Segurança por padrão

JWT, RBAC, rate limiting, sanitização e proteção contra prompt injection.

### 10\. Observabilidade

Jobs, execuções de IA e operações administrativas são rastreáveis.

### 11\. Metodologia Spec-Kit + TDD + Pareto

- **Spec-Kit:** Definir o que construir antes do código, com especificações e critérios de aceitação verificáveis.
- **TDD:** Ciclo estrito Red-Green-Refactor com `pytest` (backend) e ferramentas padronizadas (frontend); nenhuma tarefa é considerada concluída apenas porque o código foi escrito.
- **Pareto:** Priorização por maior valor e redução de riscos (P0 para alicerces jurídicos e RAG; P1 para UI e avaliação; P2 para refinamentos visuais). Pareto prioriza o trabalho, nunca justifica ausência de testes.

---

# 95\. Decisões técnicas consolidadas

## Banco

``` text
Neon PostgreSQL
pgvector
PostgreSQL Full Text Search
SQLAlchemy 2 Async
Alembic
UUID v7
(sem Qdrant ou ChromaDB)
```

## RAG

``` text
Hybrid Search
├── pgvector
└── PostgreSQL FTS

RRF
↓
Reranker
↓
Threshold
↓
Minimum evidence
↓
Dynamic context
↓
LLM
```

## LLM

``` text
Groq
Llama 3.3 70B
```

## Embeddings

``` text
paraphrase-multilingual-mpnet-base-v2
```

## API

``` text
RESTful
JSON
OpenAPI (Swagger)
SSE (Streaming)
```

## Streaming

``` text
SSE
```

## Queue

``` text
PostgreSQL
```

## Storage

``` text
S3-compatible Object Storage
```

## Backend

``` text
FastAPI
Pydantic
SQLAlchemy 2
Alembic
pytest
Monólito Modular + Arquitetura Hexagonal (Ports and Adapters)
```

## Frontend

``` text
Next.js
TypeScript
Tailwind
shadcn/ui
```

## State

``` text
Zustand
TanStack Query
```

## Forms

``` text
React Hook Form
Zod
```

## Animation

``` text
GSAP
Lenis
Three.js
```

## Testing

``` text
pytest
Playwright
```

## Deploy

``` text
Render
Neon PostgreSQL gerenciado
GitHub Actions
```

---

# 96\. O que NÃO faz parte do MVP

Para evitar crescimento desnecessário do escopo:

- microservices;
- Redis;
- gerenciamento administrativo de usuários;
- busca semântica no histórico;
- busca textual no histórico;
- WebSocket para chat (streaming via SSE);
- autenticação via localStorage;
- Qdrant e ChromaDB (busca vetorial unificada via pgvector no Neon);
- execução automática de ingestion no startup;
- múltiplas assistant messages para uma mesma resposta;
- fallback para documentos antigos/inativos;
- geração de URLs pelo LLM;
- conhecimento jurídico não fundamentado;
- aplicação exclusivamente mobile;
- Selenium;
- processamento síncrono de documentos.

---

# 97\. Resultado arquitetural

A arquitetura final pode ser resumida assim:

``` text
                         ┌───────────────────┐
                         │     Next.js       │
                         │    TypeScript     │
                         └─────────┬─────────┘
                                   │
                              HTTPS / SSE
                                   │
                         ┌─────────▼─────────┐
                         │      FastAPI      │
                         │   Modular Monolith│
                         └─────────┬─────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
             ▼                     ▼                     ▼
        Neon PostgreSQL         RAG Module          Auth/RBAC
        + pgvector + FTS             │
             │                      │
             │              ┌───────┴────────┐
             │              │                │
             │            FTS            pgvector
             │              │                │
             │              └───────┬────────┘
             │                      ▼
             │                   RRF
             │                      ▼
             │                  Reranker
             │                      ▼
             │                Context Builder
             │                      ▼
             │                   Groq LLM
             │
             ▼
          Jobs
             │
             ▼
          Worker
             │
       ┌─────┴─────┐
       ▼           ▼
    OCR/etc.   Object Storage
```

---

# 98\. Metodologia de desenvolvimento e ordem de implementação

A execução do projeto é estruturada combinando **Spec-Kit**, **Pareto** e **TDD**:

### Matriz de Priorização Pareto (Valor e Riscos)

| Prioridade | Área | Justificativa |
| :--- | :--- | :--- |
| **P0** | Fontes jurídicas e rastreabilidade | Evita respostas sem fundamentação verificável. |
| **P0** | Ingestão e processamento de documentos | Sem base de conhecimento confiável, o assistente não tem fundamento. |
| **P0** | Busca híbrida e recuperação de contexto | Determina quais informações chegam ao modelo de linguagem. |
| **P0** | Geração de respostas com citações | Núcleo do produto; deve tratar rigorosamente insuficiência de evidências. |
| **P1** | Interface de perguntas e respostas | Torna o mecanismo acessível e intuitivo para o trabalhador. |
| **P1** | Feedback, observabilidade e avaliação | Permite diagnosticar falhas, alucinações e aprimorar o RAG. |
| **P2** | Animações, personalizações e refinamentos | Melhorias visuais que aguardam a validação do fluxo essencial. |

> **Importante:** Pareto orienta a ordem de desenvolvimento com base em valor e risco, jamais justificando a ausência de testes em funcionalidades menos prioritárias.

### Ciclo de Desenvolvimento por Tarefa

``` text
IDEIA / PROBLEMA
       ↓
SPEC-KIT: SPECIFY (Problema e critérios de aceitação verificáveis)
       ↓
SPEC-KIT: PLAN (Decisões técnicas e contratos)
       ↓
SPEC-KIT: TASKS (Tarefas atômicas e testáveis)
       ↓
PRIORIZAÇÃO PARETO (P0 → P1 → P2)
       ↓
TDD: Teste que falha (RED)
       ↓
Implementação mínima (GREEN)
       ↓
Refatoração de código (REFACTOR)
       ↓
Testes de regressão
       ↓
Auditoria de critérios e conclusão
```

---

## Fase 1 — Fundação

1. Monorepo/projeto
2. Docker Compose
3. PostgreSQL + pgvector
4. FastAPI
5. SQLAlchemy
6. Alembic
7. configuração
8. health check

## Fase 2 — Identidade

1. User
2. AuthIdentity
3. bcrypt
4. JWT
5. refresh sessions
6. Google OAuth/OIDC
7. RBAC

## Fase 3 — Conversas

1. Conversation
2. Message
3. histórico
4. título
5. soft delete
6. anonymous session
7. quota

## Fase 4 — RAG

1. Document
2. DocumentChunk
3. Source
4. embeddings
5. pgvector
6. FTS
7. RRF
8. reranker
9. context builder
10. LLM provider

## Fase 5 — Ingestion

1. Object Storage
2. PDF extraction
3. OCR
4. URL extraction
5. Markdown normalization
6. metadata
7. chunking
8. embedding
9. jobs
10. worker

## Fase 6 — Chat

1. scope classifier
2. retrieval
3. generation
4. citations
5. SSE
6. interruption
7. regeneration
8. insufficient evidence

## Fase 7 — Admin

1. `/admin`
2. upload
3. URL
4. processing status
5. review
6. activation
7. deactivation
8. versioning
9. reprocessing

## Fase 8 — Frontend

1. design system
2. auth
3. chat
4. sidebar
5. citations
6. streaming
7. admin
8. responsive
9. dark/light
10. animações

## Fase 9 — Qualidade

1. unit tests
2. integration tests
3. API tests
4. E2E
5. RAG evaluation
6. security review
7. performance review

## Fase 10 — Deploy

1. staging
2. migrations
3. seed
4. ingestion inicial
5. production
6. backups
7. monitoring
8. documentação

---

# 99\. Estado final da arquitetura

O sistema será um **assistente jurídico-informativo baseado em RAG**, implementado como **monólito modular aliado à arquitetura hexagonal (Ports and Adapters)**, com:

``` text
Next.js
      ↓
FastAPI (RESTful + OpenAPI + SSE)
      ↓
Neon PostgreSQL (pgvector + FTS)
      ↓
Hybrid Retrieval
      ↓
RRF
      ↓
Reranker
      ↓
Evidence Filtering
      ↓
Groq / Llama
      ↓
SSE
      ↓
Next.js
```

A base documental será controlada por administradores, versionada e processada de forma assíncrona.

As respostas deverão ser fundamentadas em evidências recuperadas.

Quando não houver evidência suficiente, o sistema deverá **assumir a insuficiência em vez de gerar uma resposta jurídica especulativa**, oferecendo fontes oficiais registradas quando apropriado.

A arquitetura também preserva rastreabilidade entre:

``` text
Pergunta
   ↓
AIExecution
   ↓
Contexto recuperado
   ↓
DocumentChunk
   ↓
Document
   ↓
Source
   ↓
URL oficial
```

Isso permite não apenas responder ao usuário, mas também explicar **de onde veio a informação**, testar a qualidade do RAG e investigar posteriormente o comportamento do sistema.

---

# 100\. Conclusão

A entrevista arquitetural resultou em uma especificação suficientemente definida para iniciar a implementação sem precisar tomar decisões fundamentais durante a codificação.

O principal contrato arquitetural é:

``` text
Frontend não conhece a implementação do RAG.
Backend não depende da UI.
RAG não depende diretamente do provider do LLM.
LLM não é tratado como fonte de verdade.
Documentos são versionados.
Chunks são rastreáveis.
Citações apontam para evidências reais.
Jobs são assíncronos.
Estado crítico é persistente.
```

O projeto inicial já previa uma aplicação web integrada a backend e API de IA, utilizando React/Next.js, FastAPI/Python, Llama 3.3 70B via GroqCloud, embeddings, PostgreSQL/pgvector e testes automatizados.

A arquitetura consolidada mantém esse direcionamento, mas detalha os contratos e mecanismos necessários para transformar o protótipo acadêmico em uma aplicação tecnicamente coerente, testável e evolutiva.