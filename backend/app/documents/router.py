"""T023/T027: endpoints do contrato de documentos e consulta estruturada."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.chunk_schemas import DocumentChunkResponse
from app.documents.repository import DocumentRepository
from app.documents.schemas import (
    DocumentChunkListResponse,
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatusUpdate,
)
from app.documents.service import (
    DocumentNotFoundError,
    DocumentService,
    InvalidDocumentStatusError,
)
from app.shared.database import get_session
from app.sources.service import SourceNotFoundError

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo documento normativo",
    responses={404: {"description": "Fonte nao encontrada"}},
)
async def create_document(
    payload: DocumentCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentResponse:
    try:
        document = await DocumentService(DocumentRepository(session)).create(**payload.model_dump())
    except SourceNotFoundError as error:
        raise HTTPException(status_code=404, detail="Fonte nao encontrada.") from error
    return DocumentResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse, summary="Listar documentos juridicos")
async def list_documents(
    session: Annotated[AsyncSession, Depends(get_session)],
    source_id: UUID | None = None,
    is_active: bool | None = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 20,
) -> DocumentListResponse:
    items, total = await DocumentService(DocumentRepository(session)).list_documents(
        source_id=source_id,
        is_active=is_active,
        offset=offset,
        limit=limit,
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(item) for item in items],
        total=total,
    )


@router.patch(
    "/{id}/status",
    response_model=DocumentResponse,
    summary="Alterar status do documento (ativacao/desativacao)",
    responses={
        404: {"description": "Documento nao encontrado"},
        409: {"description": "Documento ainda nao esta pronto para ativacao"},
    },
)
async def update_document_status(
    id: UUID,
    payload: DocumentStatusUpdate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DocumentResponse:
    service = DocumentService(DocumentRepository(session))
    try:
        document = await (service.activate(id) if payload.is_active else service.deactivate(id))
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    except InvalidDocumentStatusError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Documento ainda nao esta pronto para ativacao.",
        ) from error
    return DocumentResponse.model_validate(document)


@router.get(
    "/{id}/chunks",
    response_model=DocumentChunkListResponse,
    summary="Listar trechos estruturados de um documento",
    responses={404: {"description": "Documento nao encontrado"}},
)
async def list_document_chunks(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    article: Annotated[str | None, Query(min_length=1, max_length=50, pattern=r"\S")] = None,
    section: Annotated[str | None, Query(min_length=1, max_length=100, pattern=r"\S")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 50,
) -> DocumentChunkListResponse:
    try:
        items, total = await DocumentService(DocumentRepository(session)).list_chunks(
            id,
            article=article,
            section=section,
            offset=offset,
            limit=limit,
        )
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    return DocumentChunkListResponse(
        items=[DocumentChunkResponse.model_validate(item) for item in items],
        total=total,
    )
