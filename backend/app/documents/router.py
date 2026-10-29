"""T023/T027: endpoints do contrato de documentos e consulta estruturada.

Os endpoints que escrevem na base de conhecimento (cadastro, ativacao,
classificacao, embedding, upload) exigem `ADMIN`: so administradores
mantêm a base de conhecimento (OVERVIEW TECNICO.md, secao 27).
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_provider import get_groq_provider
from app.ai.schemas import DocumentClassification
from app.auth.dependencies import require_admin
from app.auth.models import User
from app.documents.chunk_schemas import DocumentChunkCreate, DocumentChunkResponse
from app.documents.repository import DocumentRepository
from app.documents.schemas import (
    DocumentChunkListResponse,
    DocumentCreate,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatusUpdate,
)
from app.documents.service import (
    DocumentClassificationUnavailableError,
    DocumentHasNoChunksError,
    DocumentNotFoundError,
    DocumentService,
    DuplicateChunkIndexError,
    EmbeddingUnavailableError,
    InvalidDocumentStatusError,
    StorageUnavailableError,
)
from app.embeddings.sentence_transformer_provider import get_embedding_provider
from app.shared.database import get_session
from app.sources.service import SourceNotFoundError
from app.storage.supabase_storage import get_supabase_storage_provider

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

_RESPOSTA_SEM_CHUNKS = {"description": "Documento sem chunks ou sem provider configurado"}


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
    _admin: Annotated[User, Depends(require_admin)],
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
    _admin: Annotated[User, Depends(require_admin)],
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


@router.post(
    "/{id}/ready",
    response_model=DocumentResponse,
    summary="Marcar documento como pronto para revisao (PROCESSING -> READY)",
    responses={
        404: {"description": "Documento nao encontrado"},
        409: {"description": "Documento nao esta em PROCESSING ou nao tem chunks"},
    },
)
async def mark_document_ready(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> DocumentResponse:
    service = DocumentService(DocumentRepository(session))
    try:
        document = await service.mark_ready(id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    except (InvalidDocumentStatusError, DocumentHasNoChunksError) as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
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


@router.post(
    "/{id}/chunks",
    response_model=DocumentChunkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar um trecho manualmente (sem pipeline de ingestao ainda)",
    responses={
        404: {"description": "Documento nao encontrado"},
        409: {"description": "Indice de chunk ja cadastrado para este documento"},
    },
)
async def create_document_chunk(
    id: UUID,
    payload: DocumentChunkCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> DocumentChunkResponse:
    service = DocumentService(DocumentRepository(session))
    try:
        chunk = await service.add_chunk(id, **payload.model_dump())
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    except DuplicateChunkIndexError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return DocumentChunkResponse.model_validate(chunk)


@router.post(
    "/{id}/classify",
    response_model=DocumentClassification,
    summary="Classificar o documento via IA (Groq) e gravar em metadata_extra",
    responses={404: {"description": "Documento nao encontrado"}, 422: _RESPOSTA_SEM_CHUNKS},
)
async def classify_document(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> DocumentClassification:
    service = DocumentService(DocumentRepository(session), ai_provider=get_groq_provider())
    try:
        return await service.classify(id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    except (DocumentHasNoChunksError, DocumentClassificationUnavailableError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post(
    "/{id}/embed",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Gerar e persistir o embedding de cada chunk do documento",
    responses={404: {"description": "Documento nao encontrado"}, 422: _RESPOSTA_SEM_CHUNKS},
)
async def embed_document_chunks(
    id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> None:
    service = DocumentService(
        DocumentRepository(session), embedding_provider=get_embedding_provider()
    )
    try:
        await service.embed_chunks(id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    except (DocumentHasNoChunksError, EmbeddingUnavailableError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post(
    "/{id}/file",
    response_model=DocumentResponse,
    summary="Enviar o arquivo original (PDF) ao Supabase Storage",
    responses={404: {"description": "Documento nao encontrado"}},
)
async def attach_document_file(
    id: UUID,
    file: UploadFile,
    session: Annotated[AsyncSession, Depends(get_session)],
    _admin: Annotated[User, Depends(require_admin)],
) -> DocumentResponse:
    service = DocumentService(
        DocumentRepository(session), storage_provider=get_supabase_storage_provider()
    )
    conteudo = await file.read()
    try:
        document = await service.attach_original_file(
            id,
            filename=file.filename or "documento.pdf",
            content=conteudo,
            content_type=file.content_type or "application/octet-stream",
        )
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Documento nao encontrado.") from error
    except StorageUnavailableError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return DocumentResponse.model_validate(document)
