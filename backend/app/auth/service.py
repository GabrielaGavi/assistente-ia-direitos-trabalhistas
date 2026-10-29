"""Casos de uso de cadastro e login."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol

from app.auth.models import User, UserRole
from app.auth.security import hash_password, verify_password

__all__ = [
    "AuthService",
    "EmailAlreadyRegisteredError",
    "InvalidCredentialsError",
    "UserStore",
]


class EmailAlreadyRegisteredError(ValueError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"O email '{email}' ja esta cadastrado.")


class InvalidCredentialsError(ValueError):
    """Email inexistente ou senha incorreta.

    Deliberadamente generico: diferenciar as duas causas na mensagem
    permitiria a quem ataca descobrir quais emails existem no sistema.
    """


class UserStore(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def count(self) -> int: ...
    async def add(self, user: User) -> None: ...


class AuthService:
    def __init__(self, repository: UserStore) -> None:
        self._repository = repository

    async def register(self, *, email: str, password: str, name: str) -> User:
        async with self._repository.transaction():
            if await self._repository.get_by_email(email) is not None:
                raise EmailAlreadyRegisteredError(email)

            # Bootstrap: o MVP nao tem gerenciamento administrativo de
            # usuarios (OVERVIEW TECNICO.md, secao 9), entao precisa de algum
            # jeito de existir um primeiro ADMIN sem acesso direto ao banco.
            # O primeiro cadastro do sistema assume o papel; os demais nascem
            # USER. Corrida entre dois primeiros cadastros concorrentes pode
            # gerar dois ADMINs -- aceitavel, nao e um buraco de seguranca.
            eh_o_primeiro_usuario = await self._repository.count() == 0
            user = User(
                email=email,
                password_hash=hash_password(password),
                name=name,
                role=UserRole.ADMIN if eh_o_primeiro_usuario else UserRole.USER,
            )
            await self._repository.add(user)
            return user

    async def login(self, *, email: str, password: str) -> User:
        user = await self._repository.get_by_email(email)
        senha_valida = user is not None and verify_password(password, user.password_hash)
        if user is None or not user.is_active or not senha_valida:
            raise InvalidCredentialsError("Email ou senha invalidos.")
        return user
