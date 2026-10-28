"""Adaptador HTTP de consulta de evidencias rastreaveis (T014)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.repository import CitationRepository
from app.citations.schemas import CitationDetailResponse
from app.citations.service import CitationNotFoundError, CitationService, InvalidCitationLinkError
from app.shared.database import get_session

router = APIRouter(prefix="/api/v1/citations", tags=["citations"])


@router.get(
    "/{id}",
    response_model=CitationDetailResponse,
    summary="Consultar evidencia e metadados de uma citacao",
    responses={
        404: {"description": "Citacao nao encontrada"},
        500: {"description": "Link oficial armazenado invalido"},
    },
)
async def get_citation(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CitationDetailResponse:
    """Preserva a evidencia original, inclusive de documentos inativos."""
    service = CitationService(CitationRepository(session))
    try:
        return await service.get_by_id(id)
    except CitationNotFoundError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Citacao nao encontrada.",
        ) from erro
    except InvalidCitationLinkError as erro:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A citacao possui um link oficial invalido.",
        ) from erro
