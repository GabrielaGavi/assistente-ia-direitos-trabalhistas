# ADR-0003: Gestão de ambiente Python com uv

**Status:** Aceita
**Data:** 2026-10-11
**Decisores:** Equipe do Projeto Integrador IV (turma 6HC1)
**Tarefa relacionada:** T002 (#8)
**Feature:** `001-fontes-e-rastreabilidade`

---

## Contexto

O backend precisa de um ambiente Python reproduzível entre os integrantes do grupo.
Em trabalho acadêmico em equipe, a falha mais comum e mais cara não é um bug de
lógica: é o *"na minha máquina funciona"*. Quando cada pessoa instala versões
diferentes de SQLAlchemy ou Pydantic, testes passam para uns e falham para outros, e
o tempo some depurando o ambiente em vez do produto.

A constituição exige que *"nenhuma tarefa seja dada como concluída apenas porque o
código foi escrito — ela deve passar em todos os testes automatizados aplicáveis"*.
Isso só tem valor se a suíte rodar igual em todas as máquinas.

Restrições do contexto real:

- As máquinas da equipe são Windows.
- `requires-python = ">=3.10"`, para não excluir quem tem Python mais antigo.
- Nenhum integrante tinha Python instalado nesta máquina de desenvolvimento.

---

## Decisão

Usar **uv** como gerenciador de pacotes e de ambiente virtual do backend, com as
dependências declaradas em `backend/pyproject.toml` e as versões exatas fixadas em
`backend/uv.lock`, **versionado no Git**.

Comando único para qualquer integrante reproduzir o ambiente:

```bash
cd backend
uv sync --group dev
```

Dependências de desenvolvimento ficam em `[dependency-groups] dev`, separadas das de
runtime — a imagem de produção não carrega `pytest` nem `ruff`.

---

## Opções consideradas

### Opção A: `venv` + `pip` + `requirements.txt`

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Velocidade de instalação | Lenta |
| Reprodutibilidade | Fraca |
| Familiaridade da equipe | Alta |

**Prós:**
- Vem com o Python; nada novo para instalar.
- É o que a maioria dos materiais de curso ensina.

**Contras:**
- `requirements.txt` com versões frouxas não garante reprodutibilidade; com versões
  fixas, vira trabalho manual e some com as dependências transitivas.
- Exige dois arquivos (`requirements.txt` e `requirements-dev.txt`) e disciplina para
  mantê-los sincronizados.
- Resolução de dependências lenta.

### Opção B: Poetry

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Média |
| Velocidade de instalação | Média |
| Reprodutibilidade | Boa |
| Familiaridade da equipe | Baixa |

**Prós:**
- `poetry.lock` resolve a reprodutibilidade.
- Maduro e amplamente adotado.

**Contras:**
- Historicamente usava seção `[tool.poetry]` própria em vez do `[project]` padrão
  (PEP 621), prendendo o projeto à ferramenta.
- Resolução perceptivelmente lenta em árvores grandes.
- Precisa ser instalado à parte, igual ao uv — sem ganho de simplicidade.

### Opção C: uv (escolhida)

| Dimensão | Avaliação |
|----------|-----------|
| Complexidade | Baixa |
| Velocidade de instalação | Muito rápida |
| Reprodutibilidade | Forte |
| Familiaridade da equipe | Baixa |

**Prós:**
- `uv.lock` fixa a árvore inteira de dependências, inclusive transitivas. `uv sync`
  produz o **mesmo** ambiente em todas as máquinas.
- Escrito em Rust; instalação de ordens de magnitude mais rápida que o pip. Importa
  em TDD, onde o ciclo é repetido muitas vezes ao dia.
- Usa `[project]` do PEP 621 — padrão da linguagem, não formato proprietário.
- Um só arquivo (`pyproject.toml`) concentra dependências, grupos, configuração do
  pytest, do coverage e do ruff.
- Gerencia também a própria versão do Python, reduzindo divergência entre máquinas.

**Contras:**
- Ferramenta nova para a equipe; exige um comando novo no fluxo.
- Projeto jovem comparado ao pip.
- Mitigação: o ambiente continua sendo um `.venv` comum. Se o uv sair do caminho,
  `pip install -e .` a partir do mesmo `pyproject.toml` funciona.

---

## Análise de trade-offs

O eixo é **familiaridade** contra **reprodutibilidade**.

A Opção A é a mais familiar e a mais frágil justamente onde dói em trabalho de grupo.
A Opção B resolve a reprodutibilidade, mas custa o mesmo aprendizado da C sendo mais
lenta e menos aderente ao padrão da linguagem.

Como *nenhum* integrante já usava Poetry ou uv, a vantagem de familiaridade da Opção B
não existe neste contexto — o custo de aprendizado é o mesmo. Nesse empate, pesam a
velocidade e a aderência ao PEP 621.

O risco de adotar ferramenta jovem está contido: o artefato produzido é um `.venv`
padrão e um `pyproject.toml` padrão. A decisão é reversível com baixo custo.

---

## Consequências

**Fica mais fácil:**
- Um integrante novo sai do zero ao ambiente completo com um comando.
- Testes rodam igual em todas as máquinas e na futura CI.
- Toda a configuração do backend vive em um arquivo só.

**Fica mais difícil:**
- Cada pessoa precisa instalar o uv uma vez (`winget install astral-sh.uv`).
- Materiais de curso que assumem `pip install -r requirements.txt` não se aplicam
  diretamente.

**Precisa ser revisitado:**
- Ao configurar CI no GitHub Actions, usar a action oficial do uv com cache do `uv.lock`.
- Ao escrever o `Dockerfile` de produção, instalar apenas o grupo de runtime
  (sem `--group dev`).

---

## Itens de ação

1. [x] Criar `backend/pyproject.toml` e versionar `backend/uv.lock` (T002).
2. [x] Adicionar `.venv/` ao `.gitignore`.
3. [x] Documentar `uv sync --group dev` na seção "Como Executar" do README.
4. [ ] Usar a action oficial do uv quando houver CI.
