# Phase 0 Research: Fontes Jurídicas e Rastreabilidade Documental

**Feature**: `001-fontes-e-rastreabilidade`  
**Date**: 2026-10-09

---

## 1. Modelo de Rastreabilidade e Hierarquia Documental

### Decisão
Adotar uma hierarquia rígida de três níveis (`Source` $\rightarrow$ `Document` $\rightarrow$ `DocumentChunk`), com a entidade `Citation` associada diretamente a um `DocumentChunk` específico.

### Racional
- Uma `Source` representa a autoridade emissora institucional (ex.: Presidência da República / Planalto, TST).
- Um `Document` representa a norma jurídica consolidada (ex.: CLT, Lei nº 8.036/1990) com ciclo de vida, checksum e versionamento.
- Um `DocumentChunk` é a unidade atômica recuperável com granularidade jurídica (artigo, seção, parágrafo, página e link oficial).
- A `Citation` vincula uma mensagem do assistente ao chunk utilizado, permitindo auditar a proveniência exata de qualquer resposta gerada.

### Alternativas Consideradas
- *Associar citação diretamente ao Documento genérico:* Descartada, pois o usuário não saberia qual artigo ou parágrafo fundamentou a afirmação, comprometendo a clareza jurídica.
- *Usar apenas chunks sem entidade Document:* Descartada, pois inviabilizaria o versionamento, a auditoria de publicação e a revogação de leis inteiras.

---

## 2. Versionamento e Integridade Factual

### Decisão
Implementar versionamento imutável via número incremental (`version`), cálculo de checksum SHA-256 do texto normalizado e regra de negócio para permitir no máximo **uma única versão ativa** (`is_active = True`) por documento lógico.

### Racional
- Mudanças legislativas (reformas trabalhistas, MPs, alterações de súmulas) não podem sobrescrever o passado; versões antigas permanecem gravadas com status `INACTIVE` para auditoria de conversas históricas.
- O checksum garante idempotência: reenviar o mesmo texto não cria versão redundante.
- Somente versões com `status = READY` e `is_active = True` podem ser recuperadas pelo RAG.

---

## 3. Arquitetura do Módulo (Monólito Modular + Hexagonal)

### Decisão
Organizar os domínios `sources`, `documents` e `shared/audit` no backend FastAPI separando contratos (schemas Pydantic), casos de uso (services) e persistência (repositories SQLAlchemy 2 Async), com IDs no padrão UUID v7.

### Racional
- Alinhado aos princípios V da Constituição do Projeto e à Seção 5 do `OVERVIEW TÉCNICO.md`.
- Garante desacoplamento de provedores e permite testar as regras de versionamento e validação de fontes com testes unitários puros rápidos no `pytest`, sem depender de banco de dados real.

---

## 4. Estratégia de Testes (TDD)

### Decisão
Adotar TDD estrito com `pytest` e `pytest-asyncio`:
1. **Testes de Contrato e Schemas:** Validação de entradas e saídas Pydantic.
2. **Testes de Domínio e Serviços:** Validação de regras de versionamento, unicidade de versão ativa e cálculo de checksum.
3. **Testes de Repositório/Integração:** Persistência no Neon PostgreSQL com SQLAlchemy assíncrono.
