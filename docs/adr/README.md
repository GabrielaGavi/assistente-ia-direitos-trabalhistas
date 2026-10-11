# Architecture Decision Records (ADR)

Registro das decisões técnicas relevantes do projeto **Assistente Inteligente de
Orientação sobre Direitos Trabalhistas**.

Um ADR documenta *por que* uma decisão foi tomada, quais alternativas foram
descartadas e o que se ganha e se perde com ela. Isso atende ao Princípio I da
[constituição](../../.specify/memory/constitution.md) — *"Mudanças de escopo e
novas decisões técnicas devem ser refletidas nos artefatos de especificação"* —
e evita que uma escolha deliberada seja desfeita por engano meses depois.

## Índice

| ADR | Título | Status | Data |
|-----|--------|--------|------|
| [0001](0001-uuid-v7-como-identificador-de-dominio.md) | UUID v7 como identificador de domínio | Aceita | 2026-10-11 |
| [0002](0002-datas-timezone-aware-em-utc.md) | Datas *timezone-aware* em UTC | Aceita | 2026-10-11 |
| [0003](0003-gestao-de-ambiente-python-com-uv.md) | Gestão de ambiente Python com uv | Aceita | 2026-10-11 |
| [0004](0004-banco-postgresql-para-testes-de-integracao.md) | Banco PostgreSQL para testes de integração | Proposta | 2026-10-11 |

## Status possíveis

- **Proposta** — em discussão, ainda não vale como regra.
- **Aceita** — vigente; o código deve segui-la.
- **Depreciada** — não se aplica mais, sem substituta direta.
- **Substituída por ADR-XXXX** — trocada por uma decisão mais recente.

## Como adicionar um ADR

1. Copie o formato de um ADR existente.
2. Numere sequencialmente (`0005`, `0006`...). Números nunca são reaproveitados.
3. Registre as alternativas que foram realmente consideradas, não só a vencedora.
4. Adicione a linha no índice acima.
