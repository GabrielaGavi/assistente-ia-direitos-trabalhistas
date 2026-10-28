# Frontend Data Model: Fundação do Frontend

Estes modelos são contratos de interface. Não duplicam o modelo de persistência do backend e não expõem detalhes do RAG.

## Conversation

| Campo | Regra de interface |
|---|---|
| `id` | Identificador público e estável. |
| `title` | Pode ser definido ou atualizado pelo usuário. |
| `createdAt`, `updatedAt` | Datas formatadas no fuso do usuário; dados chegam em UTC. |
| `messages` | Ordenadas de forma determinística. |

## Message

| Campo | Regra de interface |
|---|---|
| `id` | Público, quando persistido. |
| `role` | `user` ou `assistant`. |
| `content` | Pergunta em texto ou resposta Markdown sanitizada. |
| `status` | `pending`, `streaming`, `completed`, `interrupted`, `error`, `insufficient_evidence` ou `out_of_scope`. |
| `citations` | Referências públicas associadas apenas a respostas fundamentadas. |
| `usage` | Informação opcional, apresentada somente se o backend a fornecer. |

## CitationReference

| Campo | Regra de interface |
|---|---|
| `id` | Identificador público usado para buscar o detalhe. |
| `citationNumber` | Número apresentado na resposta, iniciando em 1. |

## CitationDetail

Mapeia o endpoint existente. A interface deve preservar `original_quote` e `chunk.content` literalmente, e usar `chunk.official_url` como link específico, com `source.base_url` como origem institucional.

## UI State

| Estado | Persistência |
|---|---|
| Rascunho da mensagem | Local, enquanto o usuário edita. |
| Mensagem em streaming | Local/compartilhado enquanto não há confirmação final. |
| Sidebar e diálogo de citação | Store de interface, se atravessarem componentes. |
| Tema | Preferência local sem conteúdo sensível. |
