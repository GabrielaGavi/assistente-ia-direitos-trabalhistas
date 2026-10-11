# ADR-0005: SQLAlchemy instalado em Python puro

**Status:** Aceita
**Data:** 2026-10-11
**Decisores:** Equipe do Projeto Integrador IV (turma 6HC1)
**Tarefa relacionada:** T004 (#10)
**Feature:** `001-fontes-e-rastreabilidade`

> **Não remova `no-binary-package = ["sqlalchemy"]` do `backend/pyproject.toml`.**
> Parece uma configuração supérflua, mas sem ela o backend não importa em máquinas
> Windows 11 com Smart App Control ativo. O motivo está abaixo.

---

## Contexto

Ao executar a primeira suíte de testes que importa SQLAlchemy, a coleta do pytest
falhou antes de rodar qualquer teste:

```
ImportError: DLL load failed while importing _collections_cy:
Uma política de Controle de Aplicativo bloqueou este arquivo.
```

Investigação na máquina de desenvolvimento:

```
HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy
VerifiedAndReputablePolicyState : 1      # Smart App Control LIGADO e impondo
```

O **Smart App Control** é um recurso do Windows 11 que bloqueia binários sem
assinatura ou sem reputação estabelecida. Ele **vem ligado por padrão em instalações
limpas do Windows 11**, o que torna provável que outros integrantes do grupo
encontrem o mesmo erro.

O levantamento mostrou que o bloqueio é **seletivo**, não geral:

| Pacote | Binário nativo | Resultado |
|---|---|---|
| `pydantic_core` | Rust | Carrega |
| `asyncpg` | C | Carrega |
| `greenlet` | C | Carrega |
| `uuid_utils` | Rust | Carrega |
| `sqlalchemy` | Cython (`_collections_cy`, `_immutabledict_cy`) | **Bloqueado** |
| `httptools` | C | **Bloqueado** |

Ou seja, não é uma política contra extensões nativas em geral — são esses dois
wheels específicos que não têm reputação suficiente no serviço da Microsoft.

O detalhe decisivo: o SQLAlchemy 2.1 **distribui os módulos Cython em duas formas**
no mesmo diretório — `_collections_cy.py` (Python puro) e
`_collections_cy.cp312-win_amd64.pyd` (compilado). O import resolve para o `.pyd`
porque extensões compiladas têm precedência. Se o `.pyd` não existir, o `.py`
equivalente é usado e a biblioteca funciona normalmente.

---

## Decisão

Instalar o SQLAlchemy **a partir do código-fonte**, o que produz uma instalação sem
os arquivos compilados, declarando no `backend/pyproject.toml`:

```toml
[tool.uv]
no-binary-package = ["sqlalchemy"]
```

Adicionalmente, trocar `uvicorn[standard]` por `uvicorn` nas dependências, o que
remove o `httptools` — o outro pacote bloqueado — junto com extras que o projeto não
usa (`uvloop` não roda no Windows; `websockets` é dispensável porque o streaming
previsto é SSE).

A correção é **declarativa e reprodutível**: `uv sync` basta, sem variável de
ambiente e sem passo manual. Verificado nesta máquina — a instalação resultante tem
zero arquivos `.pyd`, e tanto `sqlalchemy` quanto `alembic` importam.

---

## Opções consideradas

### Opção A: Desligar o Smart App Control

| Dimensão | Avaliação |
|----------|-----------|
| Esforço | Baixo |
| Reversibilidade | **Nenhuma** |
| Impacto em segurança | Alto |
| Resolve para a equipe | Não |

**Prós:**
- Resolve todos os bloqueios de uma vez, inclusive futuros.

**Contras:**
- **É irreversível.** Uma vez desligado, o Smart App Control só pode ser reativado
  reinstalando o Windows.
- Reduz a proteção da máquina inteira, não apenas do projeto.
- Não resolve para os colegas — cada um teria que degradar a própria segurança.
- Desproporcional: troca uma proteção permanente do sistema por uma conveniência de
  build.

### Opção B: Apagar os arquivos `.pyd` do `site-packages`

| Dimensão | Avaliação |
|----------|-----------|
| Esforço | Baixo |
| Durabilidade | Fraca |
| Impacto em segurança | Nenhum |
| Resolve para a equipe | Não |

**Prós:**
- Funciona imediatamente e aproveita o fallback que o próprio SQLAlchemy distribui.

**Contras:**
- Qualquer `uv sync` ou reinstalação restaura os arquivos e o erro volta.
- É uma alteração manual dentro do `.venv`, invisível no repositório. Um colega
  clonando o projeto não teria como saber que precisa repetir o passo.
- Transforma um problema determinístico em um problema intermitente.

### Opção C: Instalar o SQLAlchemy a partir do source (escolhida)

| Dimensão | Avaliação |
|----------|-----------|
| Esforço | Baixo |
| Durabilidade | Forte |
| Impacto em segurança | Nenhum |
| Resolve para a equipe | Sim |

**Prós:**
- Declarado no `pyproject.toml` e versionado: vale para todos, automaticamente.
- Não exige alterar nenhuma configuração de segurança do sistema.
- Usa um caminho oficialmente suportado pelo SQLAlchemy — os módulos em Python puro
  são mantidos pelo próprio projeto, não um remendo nosso.
- Elimina a classe inteira do problema, já que nenhum `.pyd` é instalado.

**Contras:**
- Instalação um pouco mais lenta (compila a partir do sdist).
- Perde o ganho de desempenho das extensões Cython no processamento de resultados.

### Opção D: Rodar todo o backend dentro do Docker

Descartada **por ora**. Resolveria o problema, porque o contêiner é Linux e a
política do Windows não se aplica. Mas tornaria o ciclo de TDD mais lento e mais
burocrático para a equipe, e cria dependência do Docker — que, conforme o
[ADR-0004](0004-banco-postgresql-para-testes-de-integracao.md), ainda está bloqueado
nesta máquina. Continua como plano de contingência se outros pacotes forem
bloqueados.

---

## Análise de trade-offs

O eixo é **segurança do sistema** contra **desempenho da biblioteca**.

A Opção A resolve mais, mas cobra o preço mais alto e irreversível: degradar
permanentemente a proteção de uma máquina pessoal para contornar um problema de
build. Desproporcional.

A Opção B tem custo zero e durabilidade zero — resolve hoje e volta a quebrar no
próximo `uv sync`, provavelmente em um momento pior.

A Opção C paga com desempenho. Vale medir esse custo: as extensões Cython do
SQLAlchemy aceleram principalmente o processamento de grandes conjuntos de
resultados. A escala declarada no plano técnico é de ~10 fontes, centenas de normas e
milhares de chunks, com meta de **leitura de metadados em < 50ms p95** — nesse regime
o gargalo é a ida ao banco e a rede, não a materialização de objetos em memória. O
custo é real e irrelevante aqui.

Decisivo: a Opção C é a única **declarativa**. As outras duas dependem de cada
integrante lembrar de repetir um passo manual na própria máquina.

---

## Consequências

**Fica mais fácil:**
- O projeto funciona em Windows 11 com Smart App Control ativo, que é o padrão.
- Um colega clona, roda `uv sync --group dev` e tem o ambiente funcionando.
- Nenhuma configuração de segurança precisa ser alterada em máquina nenhuma.

**Fica mais difícil:**
- A instalação do SQLAlchemy fica mais lenta (compila a partir do sdist).
- O `uvicorn` perde os extras de desempenho do `[standard]`.

**Precisa ser revisitado:**
- Se a meta de < 50ms p95 não for atingida, **medir antes de culpar esta decisão**.
  O gargalo provável é consulta ou índice, não a camada de materialização.
- No `Dockerfile` de produção (Linux) esta restrição não se aplica. Vale permitir os
  wheels compilados lá, já que a política é exclusiva do Windows.
- Se outros pacotes forem bloqueados no futuro, reconsiderar a Opção D.

---

## Como reproduzir o diagnóstico

```powershell
# Estado do Smart App Control (1 = ligado e impondo, 0 = desligado, 2 = avaliação)
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy" |
    Select-Object VerifiedAndReputablePolicyState
```

```powershell
# Confirma que o SQLAlchemy roda sem as extensões compiladas (esperado: False)
.venv\Scripts\python.exe -c "from sqlalchemy.util._has_cython import HAS_CYEXTENSION; print(HAS_CYEXTENSION)"
```

---

## Itens de ação

1. [x] Declarar `no-binary-package = ["sqlalchemy"]` no `backend/pyproject.toml`.
2. [x] Trocar `uvicorn[standard]` por `uvicorn`, removendo o `httptools` bloqueado.
3. [x] Verificar que `sqlalchemy` e `alembic` importam após `uv sync` limpo.
4. [ ] Avisar os integrantes com Windows 11 sobre este ADR, já que o sintoma
       (`DLL load failed`) não sugere a causa.
5. [ ] Permitir wheels compilados no `Dockerfile` de produção, quando existir.
