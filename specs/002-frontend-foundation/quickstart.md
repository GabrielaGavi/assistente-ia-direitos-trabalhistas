# Quickstart de Validação: Fundação do Frontend

## Pré-requisitos

- Backend local disponível para validar o endpoint de citações.
- Navegador com viewport de 320 px e navegador desktop.
- Fixtures de mensagens para os estados `streaming`, `completed`, `interrupted`, `error`, `insufficient_evidence` e `out_of_scope` enquanto o contrato de chat não estiver publicado.

## Cenários de validação

1. Abrir a tela inicial e confirmar que o aviso de caráter informativo está visível e associado semanticamente ao chat.
2. Usar teclado para alcançar campo de pergunta, enviar, interromper uma geração simulada e navegar para uma citação.
3. Carregar uma resposta fixture com `[1]`, abrir a evidência e confirmar que o trecho exibido equivale ao retorno de `GET /api/v1/citations/{id}`; abrir o link específico em nova aba.
4. Simular `404`, `500`, desconexão no stream e `INSUFFICIENT_EVIDENCE`; conferir mensagem clara, preservação do texto parcial quando houver e ausência de referência inventada.
5. Executar os fluxos em 320 px e desktop, com tema claro e escuro, sem rolagem horizontal e com foco visível.
6. Quando os endpoints de conversas estiverem publicados, validar criar, abrir, renomear e excluir conversa; após cada operação, conferir a atualização do histórico sem recarregamento total.

## Critérios de conclusão

- Os cenários de citação usam somente o contrato documentado em [frontend-api-boundary.md](contracts/frontend-api-boundary.md).
- Os cenários de chat integrado só avançam após os contratos pendentes terem sido versionados pelo backend.
- Testes de componente/contrato e E2E relevantes passam antes de considerar qualquer fatia concluída.
