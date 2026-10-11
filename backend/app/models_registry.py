"""Registro central dos modelos do dominio.

O SQLAlchemy so conhece uma tabela depois que o modulo que a define e
importado. Quem precisa dessa garantia -- o `create_all` dos testes e o
`autogenerate` do Alembic -- importa este modulo e pronto.

**Ao criar um modelo novo, adicione o import aqui. Em nenhum outro lugar.**

Antes existiam dois pontos de registro (`tests/conftest.py` e
`alembic/env.py`). Esquecer um deles fazia o `autogenerate` gerar uma
migration vazia ou, pior, um `DROP TABLE` da tabela que ele nao enxergava.
Com um unico ponto, o esquecimento deixa de ser possivel.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Tasks: T006, T007 (etapa REFACTOR)
"""

from app.shared.audit import models as _audit_models  # noqa: F401

__all__: list[str] = []
