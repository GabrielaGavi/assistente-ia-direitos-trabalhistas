"""`GroqLLMProvider` sem rede: `groq.AsyncGroq` e substituido por um fake.

Nenhum teste aqui chama a API real da Groq -- custaria dinheiro e seria
instavel em CI (a chamada real foi feita manualmente uma vez, fora da suite,
para validar o schema estrito). Cobre: (1) `classify_document` monta o
`response_format` json_schema estrito corretamente e valida a resposta; (2)
`generate_answer` monta as mensagens certas; (3) erros da API (`groq.APIError`
e subclasses, incluindo `AuthenticationError` -- o cenario real que motivou
esta troca de provider) e respostas fora do schema sao convertidos em
`GroqAPIError`, sem vazar a chave.
"""

import json
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

import groq
import httpx

from app.ai.groq_provider import GroqAPIError, GroqLLMProvider
from app.ai.groq_settings import GroqSettings

TEXTO_NORMATIVO = "Art. 129. Todo empregado tera direito anual a ferias remuneradas."


def _fake_response(content: str) -> MagicMock:
    mensagem = MagicMock(content=content)
    escolha = MagicMock(message=mensagem)
    return MagicMock(choices=[escolha])


def _fake_client(content: str | None = None, erro: Exception | None = None) -> MagicMock:
    client = MagicMock()
    if erro is not None:
        client.chat.completions.create = AsyncMock(side_effect=erro)
    else:
        client.chat.completions.create = AsyncMock(return_value=_fake_response(content))
    return client


def _erro_de_autenticacao(mensagem: str) -> groq.AuthenticationError:
    resposta = httpx.Response(401, request=httpx.Request("POST", "https://api.groq.com/x"))
    return groq.AuthenticationError(mensagem, response=resposta, body=None)


class TestGroqLLMProvider(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.settings = GroqSettings(groq_api_key="chave-fake", groq_model="modelo-teste")
        self.payload = {
            "category": "ferias",
            "tags": ["periodo_aquisitivo"],
            "summary": "Trata do direito anual a ferias remuneradas.",
            "confidence": 0.92,
        }

    async def test_classifica_documento_com_schema_estrito(self) -> None:
        client = _fake_client(content=json.dumps(self.payload))

        with patch("app.ai.groq_provider.groq.AsyncGroq", return_value=client) as client_cls:
            provider = GroqLLMProvider(self.settings)
            resultado = await provider.classify_document(TEXTO_NORMATIVO)

        client_cls.assert_called_once_with(api_key="chave-fake")
        chamada = client.chat.completions.create.await_args
        self.assertEqual(chamada.kwargs["model"], "modelo-teste")
        mensagem_usuario = {"role": "user", "content": TEXTO_NORMATIVO}
        self.assertEqual(chamada.kwargs["messages"][1], mensagem_usuario)

        response_format = chamada.kwargs["response_format"]
        self.assertEqual(response_format["type"], "json_schema")
        self.assertTrue(response_format["json_schema"]["strict"])
        esquema = response_format["json_schema"]["schema"]
        self.assertEqual(esquema["additionalProperties"], False)
        self.assertEqual(
            set(esquema["required"]), {"category", "tags", "summary", "confidence"}
        )

        self.assertEqual(resultado.category, "ferias")
        self.assertEqual(resultado.tags, ["periodo_aquisitivo"])
        self.assertAlmostEqual(resultado.confidence, 0.92)

    async def test_resposta_fora_do_schema_levanta_groq_api_error(self) -> None:
        client = _fake_client(content=json.dumps({"category": "ferias"}))

        with patch("app.ai.groq_provider.groq.AsyncGroq", return_value=client):
            provider = GroqLLMProvider(self.settings)
            with self.assertRaises(GroqAPIError) as contexto:
                await provider.classify_document(TEXTO_NORMATIVO)

        self.assertIn("schema", str(contexto.exception))

    async def test_chave_invalida_levanta_groq_api_error_sem_vazar_a_chave(self) -> None:
        erro_real = _erro_de_autenticacao("Invalid API Key")
        client = _fake_client(erro=erro_real)

        with patch("app.ai.groq_provider.groq.AsyncGroq", return_value=client):
            provider = GroqLLMProvider(self.settings)
            with self.assertRaises(GroqAPIError) as contexto:
                await provider.classify_document(TEXTO_NORMATIVO)

        mensagem = str(contexto.exception)
        self.assertIn("401", mensagem)
        self.assertIn("Invalid API Key", mensagem)
        self.assertNotIn("chave-fake", mensagem)
        self.assertIs(contexto.exception.__cause__, erro_real)

    async def test_erro_de_conexao_na_geracao_de_resposta_levanta_groq_api_error(self) -> None:
        requisicao = httpx.Request("POST", "https://api.groq.com/x")
        erro_real = groq.APIConnectionError(message="Connection error.", request=requisicao)
        client = _fake_client(erro=erro_real)

        with patch("app.ai.groq_provider.groq.AsyncGroq", return_value=client):
            provider = GroqLLMProvider(self.settings)
            with self.assertRaises(GroqAPIError) as contexto:
                await provider.generate_answer("pergunta", "contexto")

        self.assertIn("Connection error", str(contexto.exception))

    async def test_gera_resposta_com_mensagens_corretas(self) -> None:
        client = _fake_client(content="Resposta fundamentada [1].")

        with patch("app.ai.groq_provider.groq.AsyncGroq", return_value=client):
            provider = GroqLLMProvider(self.settings)
            resultado = await provider.generate_answer("Quantos dias de ferias?", "[1] Art. 129.")

        self.assertEqual(resultado, "Resposta fundamentada [1].")
        chamada = client.chat.completions.create.await_args
        self.assertNotIn("response_format", chamada.kwargs)
        self.assertIn("Quantos dias de ferias?", chamada.kwargs["messages"][1]["content"])
        self.assertIn("[1] Art. 129.", chamada.kwargs["messages"][1]["content"])
