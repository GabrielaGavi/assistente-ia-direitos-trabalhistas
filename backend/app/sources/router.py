"""T023: adaptador HTTP para cadastro e consulta de fontes oficiais."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.auth.models import User
from app.shared.database import get_session
from app.sources.repository import SourceRepository
from app.sources.schemas import SourceCreate, SourceListResponse, SourceResponse
from app.sources.service import DuplicateSourceError, SourceNotFoundError, SourceService

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


@router.post(
    "",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar nova fonte oficial",
    responses={409: {"description": "Sigla ja cadastrada"}},
)
async def create_source(
    payload: SourceCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> SourceResponse:
    service = SourceService(SourceRepository(session))
    try:
        source = await service.create_source(**payload.model_dump())
    except DuplicateSourceError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ja existe uma fonte com esta sigla.",
        ) from error
    return SourceResponse.model_validate(source)


@router.get("", response_model=SourceListResponse, summary="Listar fontes oficiais")
async def list_sources(
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 20,
) -> SourceListResponse:
    items, total = await SourceService(SourceRepository(session)).list_sources(
        offset=offset,
        limit=limit,
    )
    return SourceListResponse(
        items=[SourceResponse.model_validate(item) for item in items], total=total
    )


@router.get(
    "/{id}",
    response_model=SourceResponse,
    summary="Obter detalhes de uma fonte oficial",
    responses={404: {"description": "Fonte nao encontrada"}},
)
async def get_source(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SourceResponse:
    try:
        source = await SourceService(SourceRepository(session)).get_source(id)
    except SourceNotFoundError as error:
        raise HTTPException(status_code=404, detail="Fonte nao encontrada.") from error
    return SourceResponse.model_validate(source)
