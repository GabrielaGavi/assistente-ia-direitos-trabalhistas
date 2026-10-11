# ADR-0002: Datas *timezone-aware* em UTC

**Status:** Aceita
**Data:** 2026-10-11
**Decisores:** Equipe do Projeto Integrador IV (turma 6HC1)
**Tarefa relacionada:** T003 (#9)
**Feature:** `001-fontes-e-rastreabilidade`

---

## Contexto

O [plano técnico](../../specs/001-fontes-e-rastreabilidade/plan.md) determina
*"datas em UTC"*. O [modelo de dados](../../specs/001-fontes-e-rastreabilidade/data-model.md)
já declara todos os campos temporais como `DateTime(timezone=True)`:
`created_at`, `updated_at` e `published_at`.

O peso dessas datas neste projeto não é cosmético. `published_at` é a data de
publicação oficial no Diário Oficial, e o versionamento de normas depende de saber
qual redação vigorava em determinado momento. Um erro de fuso de 3 horas pode
deslocar uma publicação para o dia anterior e fazer o sistema citar a redação errada
de um artigo — exatamente o tipo de falha que o Princípio IV (Tolerância Zero a
Alucinações Jurídicas) existe para impedir.

Há ainda um detalhe de linguagem: `datetime.utcnow()` retorna um objeto **naive**
(sem `tzinfo`), apesar do nome. Comparar um *naive* com um *aware* levanta
`TypeError`, e gravá-lo em uma coluna `timestamptz` faz o PostgreSQL assumir o fuso
da sessão — convertendo o valor silenciosamente. A função está depreciada desde o
Python 3.12.

---

## Decisão

Toda data do domínio é um `datetime` ***timezone-aware*** em **UTC**, obtido por
`app.shared.uuid.utc_now()`:

```python
def utc_now() -> datetime:
    return datetime.now(timezone.utc)
```

Regras que decorrem disso:

- **Proibido** usar `datetime.utcnow()` ou `datetime.now()` sem fuso.
- Colunas temporais são sempre `DateTime(timezone=True)` (`timestamptz` no PostgreSQL).
- Conversão para o fuso local (`America/Sao_Paulo`) é responsabilidade exclusiva da
  camada de apresentação. O backend nunca armazena nem devolve horário local.

---

## Opções consideradas

### Opção A: Horário local (`America/Sao_Paulo`) no banco

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Média |
| Risco de correção | Alto |
| Familiaridade da equipe | Alta |

**Prós:**
- Leitura direta no `psql` sem conversão mental.

**Contras:**
- O Brasil aboliu o horário de verão em 2019, mas datas históricas de publicação de
  normas **caem dentro de períodos com DST**. Intervalos ambíguos e inexistentes
  voltariam a existir para registros antigos.
- Se o backend for implantado fora do Brasil (o plano cita Render), o fuso do servidor
  diverge do fuso dos dados.
- Comparar datas entre registros gravados sob fusos diferentes vira armadilha.

### Opção B: `datetime.utcnow()` — UTC *naive*

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Risco de correção | Alto |
| Familiaridade da equipe | Alta |

**Prós:**
- Sintaxe mais curta; aparece em muito código legado e em tutoriais antigos.

**Contras:**
- O objeto não carrega `tzinfo`, então a informação de fuso é **convenção, não dado**.
  Basta um desenvolvedor assumir o contrário para corromper os registros.
- `TypeError` ao comparar com datas *aware*, que é o que o SQLAlchemy devolve ao ler
  uma coluna `timestamptz`.
- Depreciada desde o Python 3.12 — emite `DeprecationWarning` e será removida.

### Opção C: UTC *aware* via `datetime.now(timezone.utc)` (escolhida)

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Risco de correção | Baixo |
| Familiaridade da equipe | Média |

**Prós:**
- O fuso é **dado explícito no objeto**, não convenção. Elimina a classe inteira de
  bugs por suposição errada.
- UTC não tem horário de verão: todo instante é único e não ambíguo.
- Interopera diretamente com `timestamptz` e com a serialização ISO-8601 do Pydantic.
- Comparações entre datas sempre funcionam, venham do banco ou da aplicação.

**Contras:**
- Exige conversão na apresentação para exibir ao usuário brasileiro.
- Chamada mais verbosa que `utcnow()`. Mitigado pelo helper `utc_now()`.

---

## Análise de trade-offs

O trade-off real é **conveniência de leitura** contra **correção**.

A Opção A otimiza para o desenvolvedor que inspeciona o banco manualmente — um ganho
pequeno e pontual. As Opções B e C custam o mesmo em esforço, mas apenas a C torna o
fuso um dado verificável em vez de uma suposição.

Em um sistema cuja premissa é não distorcer informação jurídica, correção temporal
não é negociável. O custo de converter o fuso no frontend é trivial e fica isolado
em uma única camada.

---

## Consequências

**Fica mais fácil:**
- Comparar e ordenar datas sem risco de `TypeError` ou de erro silencioso de fuso.
- Implantar em qualquer região sem que o fuso do servidor afete os dados.
- Auditar quando uma norma foi publicada e quando foi registrada.

**Fica mais difícil:**
- Ler o banco diretamente exige conversão mental de 3 horas.
- O frontend passa a ter a responsabilidade explícita de formatar no fuso do usuário.

**Precisa ser revisitado:**
- Ao construir o frontend (Next.js), padronizar a formatação para `America/Sao_Paulo`
  em um único utilitário, em vez de espalhar conversões pelos componentes.

---

## Verificação

Coberto por `TestUtcNow` em
[`backend/tests/unit/test_shared_uuid.py`](../../backend/tests/unit/test_shared_uuid.py):
presença de `tzinfo`, `utcoffset()` igual a zero e fuso exatamente `timezone.utc`.

---

## Itens de ação

1. [x] Implementar `utc_now()` com cobertura de testes (T003).
2. [ ] Usar `utc_now` como `default` dos campos temporais dos modelos (T010, T017, T018, T025).
3. [ ] Criar utilitário único de formatação de data no frontend, quando ele existir.
