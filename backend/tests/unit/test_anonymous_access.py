"""Fluxo HTTP real com FastAPI e banco SQLite isolado, sem IA externa.

Executar com `python -m unittest discover -s tests/unit -p test_anonymous_access.py`.
Nao usa o banco PostgreSQL da fixture global do pytest.
"""

import hashlib
from datetime import timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch
from uuid import UUID

import httpx
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.anonymous.models import AnonymousSession
from app.anonymous.router import router as anonymous_router
from app.auth.models import User
from app.auth.router import router as auth_router
from app.auth.settings import get_auth_settings
from app.citations.models import Citation
from app.conversations.models import Conversation, Message
from app.conversations.router import router as conversations_router
from app.documents.chunk_models import DocumentChunk  # noqa: F401
from app.documents.models import Document  # noqa: F401
from app.rag.dependencies import get_rag_service
from app.rag.schemas import RagAnswer, RagAnswerStatus
from app.shared.database import Base, get_session
from app.shared.uuid import utc_now
from app.sources.models import Source  # noqa: F401


class AnonymousAccessTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.environment = patch.dict(
            "os.environ",
            {
                "JWT_SECRET_KEY": "test-only-secret-not-for-production-0000",
                "ANONYMOUS_QUESTIONS_LIMIT": "3",
                "ANONYMOUS_SESSION_MINUTES": "240",
            },
        )
        self.environment.start()
        get_auth_settings.cache_clear()
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        self.factory = async_sessionmaker(self.engine, expire_on_commit=False)
        async with self.engine.begin() as connection:
            await connection.run_sync(
                lambda sync: Base.metadata.create_all(
                    sync,
                    tables=[
                        User.__table__,
                        AnonymousSession.__table__,
                        Conversation.__table__,
                        Message.__table__,
                        Citation.__table__,
                    ],
                )
            )

        async def session():
            async with self.factory() as value:
                yield value

        self.rag = AsyncMock()
        self.rag.answer.return_value = RagAnswer(
            status=RagAnswerStatus.INSUFFICIENT_EVIDENCE,
            answer="Nao ha evidencia suficiente na base de teste.",
            citations=[],
        )
        app = FastAPI()
        for router in [anonymous_router, auth_router, conversations_router]:
            app.include_router(router)
        app.dependency_overrides[get_session] = session
        app.dependency_overrides[get_rag_service] = lambda: self.rag
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        )

    async def asyncTearDown(self):
        await self.client.aclose()
        await self.engine.dispose()
        get_auth_settings.cache_clear()
        self.environment.stop()

    async def guest(self):
        response = await self.client.post("/api/v1/auth/anonymous")
        self.assertEqual(response.status_code, 200, response.text)
        return {"X-Anonymous-Token": response.json()["anonymous_token"]}

    async def conversation(self, headers):
        response = await self.client.post(
            "/api/v1/conversations", json={"title": "Ferias"}, headers=headers
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["id"]

    async def test_tres_perguntas_quarta_bloqueada_e_token_apenas_hash_no_banco(self):
        headers = await self.guest()
        conversation = await self.conversation(headers)
        for _ in range(3):
            response = await self.client.post(
                f"/api/v1/conversations/{conversation}/messages",
                headers=headers,
                json={"content": "Como funcionam as ferias?"},
            )
            self.assertEqual(response.status_code, 201, response.text)
        response = await self.client.post(
            f"/api/v1/conversations/{conversation}/messages",
            headers=headers,
            json={"content": "Quarta pergunta"},
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(self.rag.answer.await_count, 3)
        resumed = await self.client.post("/api/v1/auth/anonymous", headers=headers)
        self.assertEqual(resumed.json()["questions_used"], 3)
        async with self.factory() as session:
            stored = await session.scalar(select(AnonymousSession))
            self.assertEqual(
                stored.token_hash, hashlib.sha256(headers["X-Anonymous-Token"].encode()).hexdigest()
            )

    async def test_isolamento_entre_visitantes_e_nao_autorizados_nao_gastam_quota(self):
        owner = await self.guest()
        other = await self.guest()
        conversation = await self.conversation(owner)
        for headers in [other, {}]:
            response = await self.client.get(
                f"/api/v1/conversations/{conversation}", headers=headers
            )
            self.assertEqual(response.status_code, 404 if headers else 401)
        denied = await self.client.post(
            f"/api/v1/conversations/{conversation}/messages",
            headers=other,
            json={"content": "Pergunta"},
        )
        self.assertEqual(denied.status_code, 404)
        remaining = await self.client.post("/api/v1/auth/anonymous", headers=other)
        self.assertEqual(remaining.json()["questions_used"], 0)

    async def test_cadastro_migra_mesma_conversa_sem_duplicar_mensagens(self):
        headers = await self.guest()
        conversation = await self.conversation(headers)
        await self.client.post(
            f"/api/v1/conversations/{conversation}/messages",
            headers=headers,
            json={"content": "Pergunta"},
        )
        before = (
            await self.client.get(f"/api/v1/conversations/{conversation}", headers=headers)
        ).json()
        registered = await self.client.post(
            "/api/v1/auth/register",
            headers=headers,
            json={"name": "Pessoa", "email": "pessoa@example.com", "password": "senha-teste"},
        )
        self.assertEqual(registered.status_code, 201, registered.text)
        account = {"Authorization": f"Bearer {registered.json()['access_token']}"}
        after = (
            await self.client.get(f"/api/v1/conversations/{conversation}", headers=account)
        ).json()
        self.assertEqual(before["id"], after["id"])
        self.assertEqual(before["messages"], after["messages"])
        self.assertEqual(
            (await self.client.get("/api/v1/conversations", headers=account)).json()["total"], 1
        )
        self.assertEqual(
            (
                await self.client.get(f"/api/v1/conversations/{conversation}", headers=headers)
            ).status_code,
            401,
        )
        async with self.factory() as session:
            stored = await session.get(Conversation, UUID(conversation))
            self.assertIsNone(stored.anonymous_session_id)
            self.assertEqual(str(stored.user_id), registered.json()["user"]["id"])

    async def test_login_tambem_migra_conversas_de_uma_sessao_nova(self):
        credentials = {"email": "conta@example.com", "password": "senha-teste"}
        await self.client.post("/api/v1/auth/register", json={"name": "Pessoa", **credentials})
        headers = await self.guest()
        conversation = await self.conversation(headers)
        logged_in = await self.client.post("/api/v1/auth/login", headers=headers, json=credentials)
        self.assertEqual(logged_in.status_code, 200)
        response = await self.client.get(
            f"/api/v1/conversations/{conversation}",
            headers={"Authorization": f"Bearer {logged_in.json()['access_token']}"},
        )
        self.assertEqual(response.status_code, 200)

    async def test_falha_de_provider_e_pergunta_invalida_nao_consumem_quota(self):
        headers = await self.guest()
        conversation = await self.conversation(headers)
        self.rag.answer.side_effect = RuntimeError("Provider indisponivel")
        failed = await self.client.post(
            f"/api/v1/conversations/{conversation}/messages",
            headers=headers,
            json={"content": "Pergunta"},
        )
        self.assertEqual(failed.status_code, 502)
        invalid = await self.client.post(
            f"/api/v1/conversations/{conversation}/messages",
            headers=headers,
            json={"content": "   "},
        )
        self.assertEqual(invalid.status_code, 422)
        resumed = await self.client.post("/api/v1/auth/anonymous", headers=headers)
        self.assertEqual(resumed.json()["questions_used"], 0)

    async def test_sessao_expirada_e_bearer_invalido_nao_acessam_conversa(self):
        headers = await self.guest()
        conversation = await self.conversation(headers)
        denied = await self.client.get(
            f"/api/v1/conversations/{conversation}",
            headers={**headers, "Authorization": "Bearer invalido"},
        )
        self.assertEqual(denied.status_code, 401)
        async with self.factory() as session:
            guest = await session.scalar(select(AnonymousSession))
            guest.expires_at = utc_now() - timedelta(seconds=1)
            await session.commit()
        response = await self.client.get(f"/api/v1/conversations/{conversation}", headers=headers)
        self.assertEqual(response.status_code, 401)
