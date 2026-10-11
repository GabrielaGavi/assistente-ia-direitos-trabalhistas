"""Registro central dos modelos do dominio.

O SQLAlchemy so conhece uma tabela depois que o modulo que a define e
importado. Quem precisa dessa garantia -- o `create_all` dos testes e o
`autogenerate` do Alembic -- importa este modulo e pronto.

**Ao criar um modelo novo, adicione o import aqui. Em nenhum outro lugar.**

Antes existiam dois pontos de registro (`tests/conftest.py` e
`alembic/env.py`). Esquecer um deles fazia o `autogenerate` gerar uma
migration vazia ou, pior, um `DROP TABLE` da tabela que ele nao enxergava.
Com um unico ponto, o esquecimento deixa de ser possivel.

A ordem dos imports nao importa: o SQLAlchemy resolve as chaves estrangeiras
pelo nome da tabela, depois que todas as classes foram definidas.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Tasks: T006, T007 (etapa REFACTOR)
"""

from app.citations import models as _citation_models  # noqa: F401
from app.documents import chunk_models as _chunk_models  # noqa: F401
from app.documents import models as _document_models  # noqa: F401
from app.shared.audit import models as _audit_models  # noqa: F401
from app.sources import models as _source_models  # noqa: F401

__all__: list[str] = []
