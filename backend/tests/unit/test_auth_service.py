"""`AuthService.register`/`login`: fakes para o repositorio, sem banco."""

from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from app.auth.models import User, UserRole
from app.auth.security import hash_password
from app.auth.service import AuthService, EmailAlreadyRegisteredError, InvalidCredentialsError


@asynccontextmanager
async def _sem_transacao():
    yield


def _repository(**overrides) -> SimpleNamespace:
    base = {
        "transaction": _sem_transacao,
        "get_by_email": AsyncMock(return_value=None),
        "count": AsyncMock(return_value=0),
        "add": AsyncMock(),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class TestRegister(IsolatedAsyncioTestCase):
    async def test_primeiro_usuario_do_sistema_nasce_admin(self) -> None:
        repository = _repository(count=AsyncMock(return_value=0))
        service = AuthService(repository)

        user = await service.register(email="a@a.com", password="senha123!", name="A")

        self.assertEqual(user.role, UserRole.ADMIN)
        repository.add.assert_awaited_once()

    async def test_usuarios_seguintes_nascem_user(self) -> None:
        repository = _repository(count=AsyncMock(return_value=1))
        service = AuthService(repository)

        user = await service.register(email="b@b.com", password="senha123!", name="B")

        self.assertEqual(user.role, UserRole.USER)

    async def test_senha_e_persistida_como_hash_verificavel(self) -> None:
        repository = _repository()
        service = AuthService(repository)

        user = await service.register(email="a@a.com", password="senha123!", name="A")

        self.assertNotEqual(user.password_hash, "senha123!")
        (usuario_adicionado,) = repository.add.await_args.args
        self.assertIs(usuario_adicionado, user)

    async def test_email_duplicado_levanta_erro_e_nao_adiciona(self) -> None:
        existente = User(email="a@a.com", password_hash="x", name="A", role=UserRole.USER)
        repository = _repository(get_by_email=AsyncMock(return_value=existente))
        service = AuthService(repository)

        with self.assertRaises(EmailAlreadyRegisteredError):
            await service.register(email="a@a.com", password="senha123!", name="A")

        repository.add.assert_not_awaited()


class TestLogin(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.usuario = User(
            email="a@a.com",
            password_hash=hash_password("senha123!"),
            name="A",
            role=UserRole.USER,
            is_active=True,
        )

    async def test_credenciais_corretas_devolvem_o_usuario(self) -> None:
        repository = _repository(get_by_email=AsyncMock(return_value=self.usuario))
        service = AuthService(repository)

        resultado = await service.login(email="a@a.com", password="senha123!")

        self.assertIs(resultado, self.usuario)

    async def test_senha_errada_levanta_erro_generico(self) -> None:
        repository = _repository(get_by_email=AsyncMock(return_value=self.usuario))
        service = AuthService(repository)

        with self.assertRaises(InvalidCredentialsError):
            await service.login(email="a@a.com", password="senha-errada")

    async def test_email_inexistente_levanta_o_mesmo_erro_generico(self) -> None:
        repository = _repository(get_by_email=AsyncMock(return_value=None))
        service = AuthService(repository)

        with self.assertRaises(InvalidCredentialsError):
            await service.login(email="ninguem@a.com", password="qualquer")

    async def test_usuario_inativo_nao_consegue_logar(self) -> None:
        self.usuario.is_active = False
        repository = _repository(get_by_email=AsyncMock(return_value=self.usuario))
        service = AuthService(repository)

        with self.assertRaises(InvalidCredentialsError):
            await service.login(email="a@a.com", password="senha123!")
