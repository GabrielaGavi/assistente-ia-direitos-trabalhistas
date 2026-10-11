# Guia de Setup — Assistente de Direitos Trabalhistas

Guia completo para preparar a máquina e começar a trabalhar no projeto.

**Tempo estimado:** 20 a 30 minutos na primeira vez.

> Se der erro em qualquer passo, vá direto para [Problemas conhecidos](#-problemas-conhecidos).
> Dois deles atingem praticamente todo mundo no Windows 11 e **o erro não dá pista
> nenhuma da causa**.

---

## Índice

1. [O que você vai instalar](#1-o-que-você-vai-instalar)
2. [Instalação](#2-instalação)
3. [Preparar o projeto](#3-preparar-o-projeto)
4. [Verificar se está tudo certo](#4-verificar-se-está-tudo-certo)
5. [Comandos do dia a dia](#5-comandos-do-dia-a-dia)
6. [Como pegar e resolver uma task](#6-como-pegar-e-resolver-uma-task)
7. [Problemas conhecidos](#-problemas-conhecidos)

---

## 1. O que você vai instalar

| Ferramenta | Para quê | Obrigatório |
|---|---|---|
| **Git** | Clonar o repositório e versionar | Sim |
| **Python 3.12** | Linguagem do backend | Sim |
| **uv** | Gerenciador de pacotes e ambiente virtual | Sim |
| **Docker Desktop** | Sobe o PostgreSQL 16 com `pgvector` | Sim |
| **GitHub CLI (`gh`)** | Ver e fechar issues pelo terminal | Opcional |

Não instale PostgreSQL direto na máquina. Ele roda em contêiner, o que mantém a
mesma versão e as mesmas extensões para todo o grupo.

---

## 2. Instalação

### Windows

Abra o **PowerShell** e rode:

```powershell
winget install --id Git.Git --exact --accept-package-agreements --accept-source-agreements
```

```powershell
winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements
```

```powershell
winget install --id astral-sh.uv --exact --accept-package-agreements --accept-source-agreements
```

```powershell
winget install --id Docker.DockerDesktop --exact --accept-package-agreements --accept-source-agreements
```

**Feche e abra o PowerShell** depois de instalar, para o `PATH` ser recarregado.

> O Docker Desktop no Windows exige **virtualização habilitada na BIOS**. Se ele não
> iniciar, veja [Docker Engine stopped unexpectedly](#problema-2-docker-engine-stopped-unexpectedly).

### macOS

```bash
brew install git python@3.12 uv && brew install --cask docker
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update && sudo apt install -y git python3.12 python3.12-venv curl
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Para o Docker, siga o [guia oficial do Docker Engine](https://docs.docker.com/engine/install/ubuntu/).

### Conferir a instalação

```bash
git --version && python --version && uv --version && docker --version
```

Esperado: Git 2.4x+, Python 3.12.x, uv 0.13+, Docker 2x+.

---

## 3. Preparar o projeto

### 3.1 Clonar

```bash
git clone https://github.com/GabrielaGavi/assistente-ia-direitos-trabalhistas.git
```

```bash
cd assistente-ia-direitos-trabalhistas
```

### 3.2 Subir o banco de dados

Abra o **Docker Desktop** e espere ficar *Running*. Depois, na raiz do projeto:

```bash
docker compose up -d
```

Isso cria dois bancos:

- `assistente_trabalhista` — desenvolvimento
- `assistente_trabalhista_test` — testes (a suíte cria e apaga tabelas aqui, por isso é separado)

Confirme que subiu:

```bash
docker compose ps
```

A coluna `STATUS` precisa mostrar `healthy`. Se mostrar `health: starting`, espere alguns segundos.

### 3.3 Configurar as variáveis de ambiente

```bash
cd backend
```

```bash
cp .env.example .env
```

No Windows (PowerShell), se o `cp` não funcionar:

```powershell
Copy-Item .env.example .env
```

O `.env` já vem preenchido para o banco do Docker. **Não versione esse arquivo** — ele
está no `.gitignore` de propósito, porque é onde entram as chaves de API mais adiante.

### 3.4 Instalar as dependências

Ainda dentro de `backend/`:

```bash
uv sync --group dev
```

Isso cria o `.venv` e instala tudo nas versões exatas do `uv.lock`, garantindo que o
ambiente seja idêntico ao dos outros integrantes.

### 3.5 Aplicar as migrations

```bash
uv run alembic upgrade head
```

---

## 4. Verificar se está tudo certo

Dentro de `backend/`:

```bash
uv run pytest
```

**Resultado esperado:** todos os testes passando, nenhum erro.

Se a última linha disser `N passed` sem nenhum `failed`, seu ambiente está pronto.

Confira também o lint:

```bash
uv run ruff check . && uv run ruff format --check .
```

---

## 5. Comandos do dia a dia

Todos a partir de `backend/`, exceto onde indicado.

### Testes

```bash
uv run pytest
```

```bash
uv run pytest -m unit
```

```bash
uv run pytest -m integration
```

```bash
uv run pytest --cov
```

```bash
uv run pytest tests/unit/test_shared_uuid.py -v
```

### Qualidade de código

```bash
uv run ruff check --fix . && uv run ruff format .
```

### Banco de dados

Na **raiz** do projeto:

```bash
docker compose up -d
```

```bash
docker compose down
```

Para apagar os dados e começar do zero (cuidado, é irreversível):

```bash
docker compose down -v
```

Abrir um terminal SQL no banco:

```bash
docker exec -it assistente-trabalhista-db psql -U postgres -d assistente_trabalhista
```

### Migrations

Em `backend/`, depois de criar ou alterar um modelo:

```bash
uv run alembic revision --autogenerate -m "descricao curta do que mudou"
```

```bash
uv run alembic upgrade head
```

```bash
uv run alembic downgrade -1
```

```bash
uv run alembic current
```

> **Atenção:** ao criar um modelo novo, adicione o import dele em
> `backend/app/models_registry.py`. É o único lugar. Sem isso o `autogenerate`
> gera uma migration vazia ou, pior, um `DROP TABLE` da tabela que ele não
> enxergou. Dois testes detectam esse esquecimento e dizem qual tabela ficou de
> fora: `tests/unit/test_models_registry.py` e
> `tests/integration/test_migrations.py`.

### Adicionar uma dependência nova

```bash
uv add nome-do-pacote
```

```bash
uv add --group dev nome-do-pacote
```

Commite o `pyproject.toml` **e** o `uv.lock` juntos.

---

## 6. Como pegar e resolver uma task

O projeto segue **SDD** (desenvolvimento orientado a especificação) e **TDD**
obrigatório, conforme a [constituição](../.specify/memory/constitution.md).

### Passo a passo

**1. Escolha uma task no GitHub Projects** que esteja em `Todo` e sem ninguém atribuído.
Respeite a ordem das fases — as tasks têm dependência entre si. Mova o card para
`In Progress` e se atribua.

**2. Leia a especificação antes de escrever código:**
- [`specs/001-fontes-e-rastreabilidade/spec.md`](../specs/001-fontes-e-rastreabilidade/spec.md) — requisitos e critérios
- [`specs/001-fontes-e-rastreabilidade/data-model.md`](../specs/001-fontes-e-rastreabilidade/data-model.md) — entidades e campos
- [`specs/001-fontes-e-rastreabilidade/plan.md`](../specs/001-fontes-e-rastreabilidade/plan.md) — decisões técnicas
- [`docs/adr/`](adr/README.md) — por que as coisas são do jeito que são

**3. Atualize sua branch:**

```bash
git checkout dev_SEUNOME && git pull origin main
```

**4. Siga o ciclo TDD — nessa ordem, sem pular:**

| Etapa | O que fazer | Como confirmar |
|---|---|---|
| 🔴 **RED** | Escreva o teste que descreve o comportamento esperado | `uv run pytest` **falha** |
| 🟢 **GREEN** | Escreva o mínimo de código para o teste passar | `uv run pytest` passa |
| 🔵 **REFACTOR** | Melhore o código sem mudar o comportamento | `uv run pytest` continua passando |

Rodar o teste e vê-lo falhar **antes** de implementar não é burocracia: é o que prova
que o teste realmente testa alguma coisa. Um teste escrito depois do código pode
passar por acidente e nunca detectar o bug que deveria pegar.

**5. Marque a task concluída** em `specs/001-fontes-e-rastreabilidade/tasks.md`
(troque `- [ ]` por `- [x]`).

**6. Commite** usando [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

```bash
git commit -m "feat(backend): descricao do que foi feito (T0XX)"
```

Prefixos usados no projeto: `feat`, `fix`, `test`, `docs`, `chore`, `refactor`.
Explique no corpo do commit **por que** você fez daquele jeito, não só o que fez.

**7. Antes de abrir o PR, confirme que está tudo verde:**

```bash
uv run pytest && uv run ruff check . && uv run ruff format --check .
```

**8. Abra o PR** usando o template do repositório e mova o card para `In Review`.

### Definition of Done

Uma task só está pronta quando:

- [ ] Os critérios de aceitação da especificação foram cumpridos
- [ ] Existem testes automatizados escritos e passando
- [ ] A arquitetura hexagonal foi respeitada (sem acoplamento direto com providers)
- [ ] Nenhuma credencial ou dado sensível aparece em log
- [ ] `ruff check` e `ruff format --check` passam

---

## 🔧 Problemas conhecidos

### Problema 1: `DLL load failed while importing _collections_cy`

**Sintoma** — qualquer comando que importe SQLAlchemy quebra:

```
ImportError: DLL load failed while importing _collections_cy:
Uma política de Controle de Aplicativo bloqueou este arquivo.
```

**Causa** — o **Smart App Control** do Windows 11 (ligado por padrão em instalações
novas) bloqueia binários sem reputação estabelecida, e as extensões compiladas do
SQLAlchemy caem nessa regra.

**Solução** — já está resolvida no repositório. O `backend/pyproject.toml` tem
`no-binary-package = ["sqlalchemy"]`, que instala o SQLAlchemy em Python puro. Basta
rodar:

```bash
uv sync --group dev --reinstall-package sqlalchemy
```

> **Não remova essa linha do `pyproject.toml`.** Ela parece supérflua, mas sem ela o
> backend não importa em boa parte das máquinas do grupo. Detalhes em
> [ADR-0005](adr/0005-sqlalchemy-em-python-puro.md).

**Não** desligue o Smart App Control: é irreversível sem reinstalar o Windows.

---

### Problema 2: `Docker Engine stopped unexpectedly`

**Sintoma** — o Docker Desktop não inicia e mostra algo como:

```
Docker Engine stopped unexpectedly
vpnkit-bridge handshake failed ... WSL2 não pode ser iniciado
porque a virtualização não está habilitada
```

**Causa** — a virtualização (Intel VT-x / AMD-V) está **desabilitada na BIOS/UEFI**.
O Docker no Windows roda sobre WSL2, que é uma máquina virtual.

**Como confirmar:**

```powershell
systeminfo | Select-String "Virtualiza"
```

Se aparecer `Virtualização Habilitada no Firmware: Não`, é esse o problema.
Reinstalar o Docker **não resolve**.

**Solução:**

1. Reinicie o computador
2. Entre no setup da BIOS/UEFI — normalmente `Del`, `F2`, `F10` ou `F12` na tela do fabricante
3. Procure em *Advanced* ou *CPU Configuration* por:
   - Intel: **Intel Virtualization Technology** ou **Intel VT-x**
   - AMD: **SVM Mode** ou **AMD-V**
4. Habilite, salve e saia
5. Confirme com o comando acima — deve mostrar `Sim`

Detalhes em [ADR-0004](adr/0004-banco-postgresql-para-testes-de-integracao.md).

---

### Problema 3: `connection refused` ao rodar os testes

**Causa** — o contêiner do PostgreSQL não está rodando.

```bash
docker compose ps
```

Se não aparecer nada ou o status não for `healthy`:

```bash
docker compose up -d
```

Se continuar, veja o log do banco:

```bash
docker compose logs db
```

---

### Problema 4: `python` abre a Microsoft Store

**Causa** — o Windows traz um atalho falso para `python` que só abre a loja.

**Solução** — instale o Python de verdade e feche o terminal:

```powershell
winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements
```

Se continuar, desative os aliases em
*Configurações → Aplicativos → Configurações avançadas de aplicativo → Aliases de execução de aplicativo*.

---

### Problema 5: `DATABASE_URL nao definida`

**Causa** — falta o arquivo `backend/.env`.

```bash
cd backend && cp .env.example .env
```

---

### Problema 6: `attached to a different loop` nos testes

**Causa** — alguém mudou `asyncio_default_fixture_loop_scope` ou
`asyncio_default_test_loop_scope` no `pyproject.toml`.

**Solução** — os dois precisam continuar em `"session"`. Conexões do `asyncpg` ficam
presas ao event loop que as criou; com loop por função, a primeira reutilização do
pool quebra.

---

### Problema 7: `alembic upgrade head` falha com múltiplos heads

**Causa** — duas pessoas geraram migrations a partir do mesmo ponto.

```bash
uv run alembic heads
```

Se aparecer mais de um, é preciso fazer o merge:

```bash
uv run alembic merge -m "merge de migrations" <head1> <head2>
```

Combine com quem gerou a outra migration antes de fazer isso.

---

## Ainda travado?

1. Confira se o Docker Desktop está *Running*
2. Rode `uv sync --group dev` de novo
3. Avise o grupo com a **mensagem de erro completa** — não só "não funcionou"
