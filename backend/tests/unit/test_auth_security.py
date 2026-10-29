"""Hash de senha e token de acesso: puros, sem banco e sem rede."""

from datetime import timedelta
from uuid import uuid4

import jwt
import pytest

from app.auth.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.auth.settings import AuthSettings

pytestmark = pytest.mark.unit


@pytest.fixture
def settings() -> AuthSettings:
    return AuthSettings(jwt_secret_key="segredo-de-teste", jwt_algorithm="HS256")


class TestHashPassword:
    def test_hash_e_diferente_da_senha_original(self) -> None:
        assert hash_password("senha-correta") != "senha-correta"

    def test_verify_aceita_a_senha_certa(self) -> None:
        hash_ = hash_password("senha-correta")
        assert verify_password("senha-correta", hash_) is True

    def test_verify_rejeita_senha_errada(self) -> None:
        hash_ = hash_password("senha-correta")
        assert verify_password("senha-errada", hash_) is False

    def test_hashes_do_mesmo_input_sao_diferentes(self) -> None:
        """bcrypt usa salt aleatorio -- dois hashes da mesma senha nao coincidem."""
        assert hash_password("senha-correta") != hash_password("senha-correta")


class TestAccessToken:
    def test_decode_devolve_o_user_id_usado_na_criacao(self, settings: AuthSettings) -> None:
        user_id = uuid4()
        token = create_access_token(user_id, settings)

        assert decode_access_token(token, settings) == user_id

    def test_rejeita_token_assinado_com_outra_chave(self, settings: AuthSettings) -> None:
        token = create_access_token(uuid4(), settings)
        outras_settings = AuthSettings(jwt_secret_key="outro-segredo")

        with pytest.raises(InvalidTokenError):
            decode_access_token(token, outras_settings)

    def test_rejeita_token_expirado(self, settings: AuthSettings) -> None:
        payload = {"sub": str(uuid4())}
        token_ja_expirado = jwt.encode(
            {**payload, "exp": -1},  # timestamp no passado
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )

        with pytest.raises(InvalidTokenError):
            decode_access_token(token_ja_expirado, settings)

    def test_rejeita_token_malformado(self, settings: AuthSettings) -> None:
        with pytest.raises(InvalidTokenError):
            decode_access_token("isto-nao-e-um-jwt", settings)

    def test_rejeita_token_sem_subject_valido(self, settings: AuthSettings) -> None:
        token_sem_uuid = jwt.encode(
            {"sub": "nao-e-um-uuid"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
        )

        with pytest.raises(InvalidTokenError):
            decode_access_token(token_sem_uuid, settings)

    def test_expiracao_respeita_jwt_expires_minutes(self) -> None:
        settings_curta = AuthSettings(jwt_secret_key="segredo", jwt_expires_minutes=60)
        token = create_access_token(uuid4(), settings_curta)
        payload = jwt.decode(
            token, settings_curta.jwt_secret_key, algorithms=[settings_curta.jwt_algorithm]
        )
        delta = payload["exp"] - payload["iat"]
        assert delta == timedelta(minutes=60).total_seconds()
