"""Testes do registro central de modelos.

Garantem que `app/models_registry.py` continue sendo o ponto unico de
registro. Se alguem criar um modelo novo e esquecer de adicionar o import
la, o teste abaixo falha dizendo exatamente qual tabela ficou de fora --
em vez de o problema aparecer so quando o Alembic gerar um `DROP TABLE`.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Tasks: T006, T007 (etapa REFACTOR)
"""

import importlib
from pathlib import Path

import pytest

import app
import app.models_registry  # noqa: F401
from app.shared.database import Base

pytestmark = pytest.mark.unit

RAIZ_DO_APP = Path(app.__file__).parent


def _modulos_que_podem_definir_modelos() -> list[str]:
    """Varre o pacote `app` em busca de modulos com cara de modelo."""
    return sorted(
        ".".join(("app", *caminho.relative_to(RAIZ_DO_APP).with_suffix("").parts))
        for caminho in RAIZ_DO_APP.rglob("*models*.py")
        if caminho.name != "models_registry.py"
    )


def test_registra_a_tabela_de_auditoria() -> None:
    assert "audit_logs" in Base.metadata.tables


def test_registry_cobre_todos_os_modulos_de_modelos() -> None:
    """Importar o registry deve bastar: nenhum modulo traz tabela nova depois.

    Se este teste falhar, adicione o import do modulo faltante em
    `app/models_registry.py`.
    """
    tabelas_via_registry = set(Base.metadata.tables)

    for modulo in _modulos_que_podem_definir_modelos():
        importlib.import_module(modulo)

    faltando = set(Base.metadata.tables) - tabelas_via_registry

    assert not faltando, (
        f"Tabelas nao registradas em app/models_registry.py: {sorted(faltando)}. "
        "Adicione o import do modulo correspondente la."
    )


def test_encontra_os_modulos_de_modelos_existentes() -> None:
    """Sanidade da varredura: se ela parar de achar arquivos, o teste acima
    passaria vazio e deixaria de proteger qualquer coisa."""
    modulos = _modulos_que_podem_definir_modelos()

    assert "app.shared.audit.models" in modulos
    assert "app.shared.models" in modulos
