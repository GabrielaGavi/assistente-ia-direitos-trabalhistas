"""Contratos estruturados trocados com o provider de IA.

`DocumentClassification` e passada como `response_format` ao Grok (Structured
Outputs): o modelo e obrigado a devolver um JSON que valida contra este
schema, em vez de texto livre.
"""

from pydantic import BaseModel, Field

__all__ = ["DocumentClassification"]


class DocumentClassification(BaseModel):
    """Classificacao e metadados extraidos de um trecho normativo trabalhista."""

    category: str = Field(
        description=(
            "Tema trabalhista predominante do trecho, ex.: 'ferias', "
            "'decimo_terceiro', 'jornada_de_trabalho', 'aviso_previo', 'fgts', "
            "'rescisao_contratual' ou 'outro'."
        )
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Palavras-chave adicionais relevantes para busca e filtragem.",
    )
    summary: str = Field(description="Resumo objetivo em linguagem acessível, de 1 a 3 frases.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confianca do modelo na classificacao atribuida, entre 0 e 1.",
    )
