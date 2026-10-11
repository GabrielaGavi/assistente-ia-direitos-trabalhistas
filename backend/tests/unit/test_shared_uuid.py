"""Testes unitarios do gerador de UUID v7 e dos utilitarios de data UTC.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T003
    Constituicao: Principio III (TDD) e restricao "IDs em UUID v7, datas em UTC".
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.shared.uuid import utc_now, uuid7

pytestmark = pytest.mark.unit


class TestUuid7:
    def test_retorna_instancia_uuid_da_biblioteca_padrao(self) -> None:
        """O ID deve ser um uuid.UUID nativo para interoperar com SQLAlchemy."""
        gerado = uuid7()

        assert isinstance(gerado, UUID)
        assert type(gerado) is UUID

    def test_versao_do_uuid_e_7(self) -> None:
        """A constituicao exige UUID v7, nao v4."""
        assert uuid7().version == 7

    def test_variante_rfc_4122(self) -> None:
        """Os bits de variante devem seguir a RFC 4122."""
        assert uuid7().variant == "specified in RFC 4122"

    def test_ids_gerados_sao_unicos(self) -> None:
        gerados = [uuid7() for _ in range(1_000)]

        assert len(set(gerados)) == 1_000

    def test_ids_sao_ordenaveis_por_tempo(self) -> None:
        """UUID v7 e time-ordered: a ordem de geracao deve ser a ordem crescente."""
        gerados = [uuid7() for _ in range(50)]

        assert gerados == sorted(gerados)

    def test_timestamp_embutido_corresponde_ao_momento_atual(self) -> None:
        """Os 48 bits iniciais sao o epoch em milissegundos."""
        antes = utc_now()
        gerado = uuid7()
        depois = utc_now()

        epoch_ms = gerado.int >> 80
        instante = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)

        assert antes - timedelta(seconds=1) <= instante <= depois + timedelta(seconds=1)


class TestUtcNow:
    def test_retorna_datetime_com_timezone(self) -> None:
        """Datas naive sao proibidas: toda data do dominio e aware."""
        agora = utc_now()

        assert agora.tzinfo is not None
        assert agora.utcoffset() == timedelta(0)

    def test_timezone_e_utc(self) -> None:
        assert utc_now().tzinfo == timezone.utc

    def test_avanca_no_tempo(self) -> None:
        primeiro = utc_now()
        segundo = utc_now()

        assert segundo >= primeiro
