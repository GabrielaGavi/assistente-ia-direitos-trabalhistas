"""`GrokLLMProvider` sem rede: o `xai_sdk.AsyncClient` e substituido por um fake.

Nenhum teste aqui chama a API real da xAI -- custaria dinheiro e seria instavel
em CI. Cobre dois contratos: (1) a chat e montada com o modelo e o
`response_format` corretos e a resposta e validada contra
`DocumentClassification`; (2) falhas de rede/autenticacao (`grpc.RpcError`) e
respostas fora do schema (`pydantic.ValidationError`) sao convertidas em
`GrokAPIError`, para que quem chama o provider nao precise conhecer gRPC nem
Pydantic. O segundo ponto existe porque a auditoria encontrou exatamente uma
falha de autenticacao (`XAI_API_KEY` invalida) chegando sem tratamento.
"""

import json
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

import grpc

from app.ai.grok_provider import GrokAPIError, GrokLLMProvider
from app.ai.schemas import DocumentClassification
from app.ai.settings import GrokSettings

TEXTO_NORMATIVO = "Art. 129. Todo empregado tera direito anual a ferias remuneradas."


class _ErroRpcFalso(grpc.RpcError):
    """Imita o formato real do erro que a xAI devolve para chave invalida."""

    def __init__(self, codigo: grpc.StatusCode, detalhes: str) -> None:
        self._codigo = codigo
        self._detalhes = detalhes

    def code(self) -> grpc.StatusCode:
        return self._codigo

    def details(self) -> str:
        return self._detalhes


def _fake_client(response_content: str | None = None, erro: Exception | None = None) -> MagicMock:
    fake_chat = MagicMock()
    fake_chat.append = MagicMock()
    if erro is not None:
        fake_chat.sample = AsyncMock(side_effect=erro)
    else:
        fake_chat.sample = AsyncMock(return_value=MagicMock(content=response_content))
    client = MagicMock()
    client.chat.create = MagicMock(return_value=fake_chat)
    return client


class TestGrokLLMProvider(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.settings = GrokSettings(xai_api_key="chave-fake", xai_model="grok-4-test")
        self.payload = {
            "category": "ferias",
            "tags": ["periodo_aquisitivo"],
            "summary": "Trata do direito anual a ferias remuneradas.",
            "confidence": 0.92,
        }

    async def test_classifica_documento_usando_structured_outputs(self) -> None:
        client = _fake_client(response_content=json.dumps(self.payload))

        with patch("app.ai.grok_provider.AsyncClient", return_value=client) as client_cls:
            provider = GrokLLMProvider(self.settings)
            resultado = await provider.classify_document(TEXTO_NORMATIVO)

        client_cls.assert_called_once_with(api_key="chave-fake")
        client.chat.create.assert_called_once_with(
            model="grok-4-test", response_format=DocumentClassification
        )
        self.assertEqual(client.chat.create.return_value.append.call_count, 2)
        self.assertIsInstance(resultado, DocumentClassification)
        self.assertEqual(resultado.category, "ferias")
        self.assertEqual(resultado.tags, ["periodo_aquisitivo"])
        self.assertAlmostEqual(resultado.confidence, 0.92)

    async def test_resposta_fora_do_schema_levanta_grok_api_error(self) -> None:
        client = _fake_client(response_content=json.dumps({"category": "ferias"}))

        with patch("app.ai.grok_provider.AsyncClient", return_value=client):
            provider = GrokLLMProvider(self.settings)
            with self.assertRaises(GrokAPIError) as contexto:
                await provider.classify_document(TEXTO_NORMATIVO)

        self.assertIn("schema", str(contexto.exception))

    async def test_chave_invalida_levanta_grok_api_error_sem_vazar_a_chave(self) -> None:
        erro_real = _ErroRpcFalso(
            grpc.StatusCode.INVALID_ARGUMENT,
            "Incorrect API key provided. You can obtain an API key from https://console.x.ai.",
        )
        client = _fake_client(erro=erro_real)

        with patch("app.ai.grok_provider.AsyncClient", return_value=client):
            provider = GrokLLMProvider(self.settings)
            with self.assertRaises(GrokAPIError) as contexto:
                await provider.classify_document(TEXTO_NORMATIVO)

        mensagem = str(contexto.exception)
        self.assertIn("INVALID_ARGUMENT", mensagem)
        self.assertIn("Incorrect API key provided", mensagem)
        self.assertNotIn("chave-fake", mensagem)
        self.assertIs(contexto.exception.__cause__, erro_real)

    async def test_falha_de_rede_na_geracao_de_resposta_levanta_grok_api_error(self) -> None:
        erro_real = _ErroRpcFalso(grpc.StatusCode.UNAVAILABLE, "upstream connect error")
        client = _fake_client(erro=erro_real)

        with patch("app.ai.grok_provider.AsyncClient", return_value=client):
            provider = GrokLLMProvider(self.settings)
            with self.assertRaises(GrokAPIError) as contexto:
                await provider.generate_answer("pergunta", "contexto")

        self.assertIn("UNAVAILABLE", str(contexto.exception))
