# Frontend/API Boundary

## Regra de fronteira

O frontend consome somente identificadores e campos públicos da API. Não recebe identificadores internos de `DocumentChunk`, embeddings, parâmetros de busca, prompts ou decisões internas de reranking.

## Contrato implementado: detalhe de citação

`GET /api/v1/citations/{id}` já está exposto pelo backend.

Resposta de sucesso (`200`):

```json
{
  "id": "uuid",
  "citation_number": 1,
  "original_quote": "trecho original preservado",
  "chunk": {
    "id": "uuid-interno-nao-usado-para-navegacao",
    "document_id": "uuid",
    "chunk_index": 0,
    "content": "texto literal",
    "official_url": "https://fonte.gov.br/...",
    "article": "Art. 1º",
    "section": null,
    "paragraph": null
  },
  "source": {
    "id": "uuid",
    "name": "Nome da fonte",
    "short_name": "Sigla",
    "base_url": "https://fonte.gov.br",
    "description": null,
    "created_at": "2026-10-27T00:00:00Z"
  }
}
```

Erros esperados: `404` para referência inexistente e `500` quando a evidência cadastrada possui URL oficial inválida. A interface não deve inferir outra URL nesses casos.

## Contrato requerido: envio e streaming de mensagem

Ainda não implementado; precisa ser definido e publicado pelo backend antes da fatia de integração.

Requisito mínimo do request:

```json
{ "message": "Quantos dias de férias eu tenho?" }
```

Eventos SSE mínimos:

| Evento | Payload público mínimo | Efeito na UI |
|---|---|---|
| `status` | `status`, `message` | Exibe “Consultando fontes” ou “Elaborando resposta”. |
| `text` | `delta` | Acrescenta texto à resposta provisória. |
| `sources` | `citations: [{ id, citation_number }]` | Habilita as referências renderizadas na resposta. |
| `done` | `message`, `status`, `citations`, `usage?` | Finaliza e persiste visualmente a resposta. |
| `error` | `code`, `message`, `details?` | Finaliza com falha compreensível. |

Status terminais mínimos: `COMPLETED`, `INSUFFICIENT_EVIDENCE`, `OUT_OF_SCOPE`, `INTERRUPTED`, `FAILED`.

## Contratos a publicar antes das fatias seguintes

- Conversas: criar, listar, consultar, renomear, excluir e obter mensagens paginadas.
- Sessão: bootstrap anônimo, quota restante, login/logout, refresh e autorização de administrador.
- Controle de geração: endpoint ou semântica inequívoca para interromper/regenerar.
- Administração: listagem e mutações de fontes/documentos, respeitando papéis.
- Transversal: CORS, origem permitida, formato padronizado de erros e versionamento de API.
