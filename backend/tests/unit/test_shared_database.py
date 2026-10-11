"""Testes unitarios da camada de acesso assincrono ao banco.

Validam a *configuracao* do engine, da fabrica de sessoes e da Base declarativa
sem abrir conexao com o PostgreSQL -- o SQLAlchemy so conecta de fato na
primeira operacao, entao a configuracao e verificavel isoladamente.
O comportamento transacional contra banco real e coberto na T006.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T004
    ADR: 0002 (datas timezone-aware em UTC)
"""

from datetime import datetime

import pytest
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.shared.database import Base, create_database_engine, create_session_factory

pytestmark = pytest.mark.unit

URL_VALIDA = "postgresql+asyncpg://user:pass@localhost:5432/teste"


class TestBaseDeclarativa:
    def test_e_uma_declarative_base(self) -> None:
        assert issubclass(Base, DeclarativeBase)

    def test_possui_metadata_para_migrations(self) -> None:
        """O Alembic (T007) depende de Base.metadata para autogerar migrations."""
        assert Base.metadata is not None

    def test_datetime_mapeia_para_timestamp_com_timezone(self) -> None:
        """Garante o ADR-0002 por construcao: nenhuma coluna de data nasce naive.

        Sem o type_annotation_map, `Mapped[datetime]` geraria TIMESTAMP WITHOUT
        TIME ZONE e o fuso seria perdido silenciosamente na gravacao.
        """

        class ModeloDeProva(Base):
            __tablename__ = "modelo_de_prova_t004"

            id: Mapped[int] = mapped_column(primary_key=True)
            criado_em: Mapped[datetime]

        coluna = ModeloDeProva.__table__.c.criado_em

        assert isinstance(coluna.type, TIMESTAMP)
        assert coluna.type.timezone is True


class TestCreateDatabaseEngine:
    def test_retorna_async_engine(self) -> None:
        engine = create_database_engine(URL_VALIDA)

        assert isinstance(engine, AsyncEngine)

    def test_preserva_a_url_recebida(self) -> None:
        engine = create_database_engine(URL_VALIDA)

        assert engine.url.database == "teste"
        assert engine.url.host == "localhost"

    def test_habilita_pool_pre_ping(self) -> None:
        """A Neon encerra conexoes ociosas; sem pre_ping a aplicacao usaria
        uma conexao morta e falharia na primeira query apos o periodo ocioso."""
        engine = create_database_engine(URL_VALIDA)

        assert engine.pool._pre_ping is True

    def test_echo_desligado_por_padrao(self) -> None:
        assert create_database_engine(URL_VALIDA).echo is False

    def test_echo_pode_ser_ligado(self) -> None:
        assert create_database_engine(URL_VALIDA, echo=True).echo is True

    @pytest.mark.parametrize(
        "url_sincrona",
        [
            "postgresql://user:pass@localhost:5432/teste",
            "postgresql+psycopg2://user:pass@localhost:5432/teste",
            "sqlite:///local.db",
        ],
    )
    def test_rejeita_driver_sincrono(self, url_sincrona: str) -> None:
        """Erro comum: colar `postgresql://` no .env.

        Sem essa guarda, a falha so apareceria no primeiro acesso ao banco, com
        uma mensagem interna do SQLAlchemy dificil de relacionar a causa.
        """
        with pytest.raises(ValueError, match="assincrono"):
            create_database_engine(url_sincrona)

    def test_mensagem_de_erro_cita_o_driver_esperado(self) -> None:
        with pytest.raises(ValueError, match=r"postgresql\+asyncpg"):
            create_database_engine("postgresql://user:pass@localhost/teste")

    @pytest.mark.parametrize(
        "url_invalida",
        [
            "nao-e-uma-url",
            "postgresql+driver_inexistente://user:pass@localhost/teste",
            "",
        ],
    )
    def test_rejeita_url_malformada(self, url_invalida: str) -> None:
        """URL quebrada tambem precisa falhar cedo, com mensagem util."""
        with pytest.raises(ValueError, match="invalida"):
            create_database_engine(url_invalida)

    def test_mensagem_de_erro_nao_vaza_a_senha(self) -> None:
        """A mensagem vai para log; a Definition of Done proibe credencial em log."""
        with pytest.raises(ValueError) as erro:
            create_database_engine("postgresql://usuario:SENHA_SECRETA@host/banco")

        assert "SENHA_SECRETA" not in str(erro.value)


class TestCreateSessionFactory:
    def test_retorna_async_sessionmaker(self) -> None:
        fabrica = create_session_factory(create_database_engine(URL_VALIDA))

        assert isinstance(fabrica, async_sessionmaker)

    def test_produz_async_session(self) -> None:
        fabrica = create_session_factory(create_database_engine(URL_VALIDA))

        assert isinstance(fabrica(), AsyncSession)

    def test_expire_on_commit_desligado(self) -> None:
        """Com expire_on_commit=True, acessar um atributo depois do commit
        dispara recarga lazy. Em codigo assincrono isso levanta MissingGreenlet
        quando o FastAPI serializa a resposta apos a transacao."""
        fabrica = create_session_factory(create_database_engine(URL_VALIDA))

        assert fabrica.kw["expire_on_commit"] is False

    def test_vinculada_ao_engine_recebido(self) -> None:
        engine = create_database_engine(URL_VALIDA)
        fabrica = create_session_factory(engine)

        assert fabrica.kw["bind"] is engine
