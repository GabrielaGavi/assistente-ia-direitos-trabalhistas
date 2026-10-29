"""`ConversationService`: fakes para o repositorio e para o `RagService`.

O ponto central testado aqui e a orquestracao: a mensagem do usuario e
persistida antes da chamada ao RAG (fora de transacao), e a mensagem da IA
mais as citacoes sao persistidas juntas -- com status `FAILED`, sem
citacoes, quando o RAG falha.
"""

from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from uuid import uuid4

from app.conversations.models import MessageRole, MessageStatus
from app.conversations.service import (
    ChatGenerationError,
    ConversationNotFoundError,
    ConversationService,
)
from app.rag.schemas import RagAnswer, RagAnswerStatus, RetrievedChunk
from app.shared.uuid import utc_now, uuid7


@asynccontextmanager
async def _sem_transacao():
    yield


async def _simular_flush(entidade) -> None:
    """`id`/`created_at` dos mixins so sao preenchidos no flush real; aqui
    ele nunca acontece (o repositorio e um fake), entao o teste simula isso."""
    if entidade.id is None:
        entidade.id = uuid7()
    if getattr(entidade, "created_at", None) is None:
        entidade.created_at = utc_now()


def _repository(**overrides) -> SimpleNamespace:
    base = {
        "transaction": _sem_transacao,
        "add_conversation": AsyncMock(side_effect=_simular_flush),
        "get_conversation": AsyncMock(return_value=None),
        "list_conversations": AsyncMock(return_value=([], 0)),
        "add_message": AsyncMock(side_effect=_simular_flush),
        "list_messages": AsyncMock(return_value=[]),
        "add_citation": AsyncMock(side_effect=_simular_flush),
        "list_citations_by_message_ids": AsyncMock(return_value=[]),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _conversa(user_id):
    return SimpleNamespace(
        id=uuid4(), user_id=user_id, title="Conversa", created_at=None, updated_at=None
    )


class TestSendMessage(IsolatedAsyncioTestCase):
    async def test_conversa_inexistente_levanta_erro_sem_chamar_o_rag(self) -> None:
        repository = _repository(get_conversation=AsyncMock(return_value=None))
        rag_service = AsyncMock()
        service = ConversationService(repository, rag_service)

        with self.assertRaises(ConversationNotFoundError):
            await service.send_message(uuid4(), uuid4(), "pergunta")

        rag_service.answer.assert_not_awaited()
        repository.add_message.assert_not_awaited()

    async def test_conversa_de_outro_usuario_levanta_o_mesmo_erro(self) -> None:
        dono = uuid4()
        outro_usuario = uuid4()
        repository = _repository(get_conversation=AsyncMock(return_value=_conversa(dono)))
        service = ConversationService(repository, AsyncMock())

        with self.assertRaises(ConversationNotFoundError):
            await service.send_message(uuid4(), outro_usuario, "pergunta")

    async def test_caminho_feliz_persiste_mensagens_e_citacoes(self) -> None:
        user_id = uuid4()
        conversa = _conversa(user_id)
        repository = _repository(get_conversation=AsyncMock(return_value=conversa))
        chunk = RetrievedChunk(
            id=uuid4(),
            document_id=uuid4(),
            content="Art. 129. Ferias.",
            official_url="https://example.org/clt",
        )
        resposta = RagAnswer(
            status=RagAnswerStatus.ANSWERED, answer="Resposta [1].", citations=[chunk]
        )
        rag_service = AsyncMock(answer=AsyncMock(return_value=resposta))
        service = ConversationService(repository, rag_service)

        resultado = await service.send_message(conversa.id, user_id, "Quantos dias de ferias?")

        self.assertEqual(resultado.role, MessageRole.ASSISTANT)
        self.assertEqual(resultado.status, MessageStatus.COMPLETED)
        self.assertEqual(resultado.content, "Resposta [1].")
        self.assertEqual(len(resultado.citations), 1)
        self.assertEqual(resultado.citations[0].citation_number, 1)
        self.assertEqual(resultado.citations[0].original_quote, "Art. 129. Ferias.")

        self.assertEqual(repository.add_message.await_count, 2)
        mensagens_salvas = [chamada.args[0] for chamada in repository.add_message.await_args_list]
        self.assertEqual(mensagens_salvas[0].role, MessageRole.USER)
        self.assertEqual(mensagens_salvas[0].content, "Quantos dias de ferias?")
        self.assertEqual(mensagens_salvas[1].role, MessageRole.ASSISTANT)
        repository.add_citation.assert_awaited_once()

    async def test_falha_do_rag_persiste_mensagem_failed_sem_citacoes(self) -> None:
        user_id = uuid4()
        conversa = _conversa(user_id)
        repository = _repository(get_conversation=AsyncMock(return_value=conversa))
        rag_service = AsyncMock(answer=AsyncMock(side_effect=RuntimeError("Groq indisponivel")))
        service = ConversationService(repository, rag_service)

        with self.assertRaises(ChatGenerationError):
            await service.send_message(conversa.id, user_id, "pergunta")

        self.assertEqual(repository.add_message.await_count, 2)
        mensagem_assistente = repository.add_message.await_args_list[1].args[0]
        self.assertEqual(mensagem_assistente.role, MessageRole.ASSISTANT)
        self.assertEqual(mensagem_assistente.status, MessageStatus.FAILED)
        repository.add_citation.assert_not_awaited()
