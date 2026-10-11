# ADR-0001: UUID v7 como identificador de domínio

**Status:** Aceita
**Data:** 2026-10-11
**Decisores:** Equipe do Projeto Integrador IV (turma 6HC1)
**Tarefa relacionada:** T003 (#9)
**Feature:** `001-fontes-e-rastreabilidade`

---

## Contexto

O [plano técnico](../../specs/001-fontes-e-rastreabilidade/plan.md) impõe como
restrição: *"IDs gerados em formato UUID v7"*. Todas as entidades do domínio
(`Source`, `Document`, `DocumentChunk`, `Citation`) usam UUID como chave primária.

Três forças pesam nessa escolha:

1. **Volume e crescimento do índice.** A especificação prevê *"milhares de chunks"*,
   e cada chunk é referenciado por citações. A chave primária será inserida em
   massa durante a ingestão de normas.
2. **Desempenho de leitura.** A meta declarada é *"leitura de metadados de fontes e
   chunks em < 50ms p95"*.
3. **Geração distribuída.** O ID precisa ser gerado pela aplicação (não pelo banco),
   para que o serviço monte o objeto completo antes do `INSERT` e mantenha o domínio
   desacoplado da persistência (Princípio V — Ports and Adapters).

O problema prático: a biblioteca padrão do Python expõe apenas UUID v1, v3, v4 e v5
até a versão 3.13. UUID v6/v7/v8 (RFC 9562) só entram na `stdlib` no Python 3.14,
acima do `requires-python = ">=3.10"` acordado com a equipe.

---

## Decisão

Gerar todos os identificadores de domínio como **UUID v7**, por meio da função
`app.shared.uuid.uuid7()`, que delega a geração à biblioteca `uuid-utils` e
**converte o resultado para `uuid.UUID` nativo** antes de devolvê-lo.

```python
def uuid7() -> UUID:
    return UUID(bytes=uuid_utils.uuid7().bytes)
```

Nenhuma camada pode usar `uuid.uuid4()` para chaves de domínio.

---

## Opções consideradas

### Opção A: UUID v4 da biblioteca padrão

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Dependências | Nenhuma |
| Desempenho de escrita | Ruim |
| Familiaridade da equipe | Alta |

**Prós:**
- Zero dependências externas; já vem no Python.
- É o padrão que a maioria dos tutoriais usa, então a equipe já conhece.

**Contras:**
- Totalmente aleatório. Cada `INSERT` cai em uma página arbitrária do índice B-tree,
  causando fragmentação e *page splits*. Em tabelas grandes isso degrada a escrita
  e infla o índice.
- Não é ordenável. Paginar por "mais recentes" exige um índice adicional em
  `created_at`.
- **Descumpre a restrição explícita do plano técnico.**

### Opção B: `BIGSERIAL` (inteiro sequencial do PostgreSQL)

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Dependências | Nenhuma |
| Desempenho de escrita | Ótimo |
| Familiaridade da equipe | Alta |

**Prós:**
- Melhor localidade de índice possível e chave mais compacta (8 bytes contra 16).

**Contras:**
- O ID só existe **depois** do `INSERT`, o que obriga o serviço a conhecer o ciclo de
  vida da transação e fere o desacoplamento exigido pelo Princípio V.
- IDs sequenciais são enumeráveis: expõem volume de dados e permitem varrer recursos
  pela URL (`/documents/1`, `/documents/2`...).
- Descumpre a restrição do plano técnico.

### Opção C: UUID v7 via `uuid-utils` (escolhida)

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Dependências | 1 (`uuid-utils`, extensão em Rust) |
| Desempenho de escrita | Bom |
| Familiaridade da equipe | Média |

**Prós:**
- Os 48 bits mais significativos carregam o *epoch* em milissegundos, então os IDs
  são **monotonicamente crescentes**. As inserções concentram-se na borda direita do
  índice B-tree, preservando a localidade de escrita.
- Ordenável por tempo sem índice extra: `ORDER BY id` já é ordem cronológica.
- Gerado na aplicação, antes do `INSERT`, mantendo o domínio desacoplado.
- Mantém a opacidade do v4 — os 74 bits restantes são aleatórios, então não é enumerável.
- Atende à restrição do plano técnico.

**Contras:**
- Acrescenta uma dependência.
- Vaza o instante de criação do registro. Irrelevante aqui: os dados são legislação
  pública e as datas já são campos explícitos (`created_at`, `published_at`).

### Opção D: UUID v7 implementado à mão

Descartada. Exigiria manipulação manual de bits de versão e variante, mais um
contador para garantir monotonicidade sub-milissegundo — código de infraestrutura
delicado, sem valor didático para o projeto e com risco de bug sutil em produção.

---

## Análise de trade-offs

O eixo central é **localidade de índice** contra **desacoplamento do domínio**.

- `BIGSERIAL` vence em localidade, mas perde em desacoplamento (o ID depende do banco).
- UUID v4 vence em simplicidade, mas perde nos dois outros eixos.
- UUID v7 é o único que entrega os dois: ordenação temporal *e* geração na aplicação.

O custo é uma dependência e 8 bytes a mais por chave em relação ao `BIGSERIAL` —
desprezível na escala do projeto (~10 fontes, centenas de normas, milhares de chunks).

A conversão para `uuid.UUID` nativo é parte essencial da decisão: sem ela, o tipo
`uuid_utils.UUID` vazaria para os modelos SQLAlchemy e schemas Pydantic, acoplando
todo o domínio a uma biblioteca de terceiros. Com a conversão, trocar `uuid-utils`
por `uuid.uuid7()` da `stdlib` quando o projeto migrar para o Python 3.14 será uma
mudança de uma linha, contida em um único arquivo.

---

## Consequências

**Fica mais fácil:**
- Ordenar e paginar por data de criação sem índice adicional.
- Migrar para a `stdlib` no Python 3.14 — basta alterar `app/shared/uuid.py`.
- Manter inserções em massa performáticas durante a ingestão de normas.

**Fica mais difícil:**
- Nada de relevante. A API pública (`uuid7() -> UUID`) é idêntica à de `uuid.uuid4`.

**Precisa ser revisitado:**
- Quando o projeto adotar Python 3.14, substituir `uuid-utils` por `uuid.uuid7()`.
- Se algum dado sensível passar a ser identificado por UUID v7, reavaliar o
  vazamento do instante de criação. Não é o caso da legislação pública.

---

## Verificação

A decisão é verificada por [`backend/tests/unit/test_shared_uuid.py`](../../backend/tests/unit/test_shared_uuid.py),
que cobre:

- tipo `uuid.UUID` nativo (garante o desacoplamento descrito acima);
- `version == 7` e variante RFC 4122;
- unicidade em 1.000 gerações consecutivas;
- **ordenação cronológica** — o teste que comprova o benefício de índice;
- correspondência entre o *timestamp* embutido e o instante real de geração.

---

## Itens de ação

1. [x] Implementar `app/shared/uuid.py` com cobertura de testes (T003).
2. [ ] Usar `uuid7()` como `default` das chaves primárias nos modelos SQLAlchemy (T010, T017, T018, T025).
3. [ ] Revisitar quando o projeto migrar para Python 3.14.
