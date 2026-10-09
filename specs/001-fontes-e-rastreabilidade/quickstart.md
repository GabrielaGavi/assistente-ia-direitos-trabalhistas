# Quickstart Guide: Validação de Fontes e Rastreabilidade

**Feature**: `001-fontes-e-rastreabilidade`  
**Date**: 2026-10-09

---

## 1. Pré-requisitos
- Python 3.10+
- Ambiente virtual configurado com dependências do backend
- Acesso à base Neon PostgreSQL (ou PostgreSQL de testes com extensão `uuid-ossp`)

## 2. Cenário de Validação End-to-End

### Cenário 1: Cadastro e Versionamento de Norma Legal
1. Criar a Fonte Oficial "Planalto":
   - `POST /api/v1/sources` com `name="Presidência da República"`, `short_name="Planalto"`, `base_url="https://www.planalto.gov.br"`.
2. Registrar a "CLT" (versão 1):
   - `POST /api/v1/documents` com `logical_name="clt"`, `title="Consolidação das Leis do Trabalho"`.
   - Verificar que a versão inicial é `1` e `status="PROCESSING"`.
3. Inserir trecho estruturado (Art. 130 da CLT):
   - Verificar campos `article="Art. 130"`, `section="Capítulo IV"`, `official_url="https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"`.
4. Ativar o documento:
   - `PATCH /api/v1/documents/{id}/status` com `is_active=true`.
   - Confirmar transição para `is_active=true` e status `ACTIVE`.
5. Tentar cadastrar nova redação (versão 2):
   - Confirmar que a nova versão recebe `version=2`.
   - Ao ativar a v2, verificar que a v1 passa automaticamente para `is_active=false`.

### Cenário 2: Validação de Citação Rastreável
1. Criar uma citação vinculada ao chunk do Art. 130.
2. Inspecionar a citação via `GET /api/v1/citations/{id}`.
3. Assegurar que o trecho retornado é o texto literal do chunk, com todos os metadados oficiais e sem modificações no texto jurídico.

---

## 3. Comandos de Execução de Testes
```bash
# Executar a suíte de testes unitários e de integração do domínio de fontes
pytest tests/unit/sources tests/unit/documents -v
```
