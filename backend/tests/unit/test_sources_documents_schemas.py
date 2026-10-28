"""T019/T020: contratos de entrada e serializacao, sem banco."""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.documents.models import Document, DocumentStatus
from app.documents.schemas import DocumentCreate, DocumentResponse, DocumentStatusUpdate
from app.shared.uuid import uuid7
from app.sources.models import Source
from app.sources.schemas import SourceCreate, SourceResponse

pytestmark = pytest.mark.unit


@pytest.fixture(scope="session", autouse=True)
def _schema() -> None:
    """Dispensa somente neste modulo a fixture PostgreSQL global."""


def source_data() -> dict:
    return {"name": "Planalto", "short_name": "Planalto", "base_url": "https://planalto.gov.br"}


def document_data() -> dict:
    return {
        "source_id": uuid7(),
        "title": "CLT",
        "logical_name": "clt",
        "checksum_sha256": "A" * 64,
    }


def test_source_defaults_and_url_are_preserved() -> None:
    payload = SourceCreate(**source_data())
    assert payload.description is None
    assert payload.model_dump()["base_url"] == source_data()["base_url"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("name", "  "),
        ("name", "x" * 256),
        ("short_name", ""),
        ("short_name", "\t"),
        ("short_name", "x" * 51),
        ("base_url", "not-a-url"),
        ("base_url", "file:///etc/passwd"),
        ("base_url", "https://example.org/" + "x" * 500),
    ],
)
def test_invalid_source(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        SourceCreate(**(source_data() | {field: value}))


@pytest.mark.parametrize("field", ["name", "short_name", "base_url"])
def test_required_source_fields(field: str) -> None:
    data = source_data()
    del data[field]
    with pytest.raises(ValidationError):
        SourceCreate(**data)


def test_document_defaults_and_aware_publication() -> None:
    payload = DocumentCreate(**document_data())
    assert payload.published_at is None
    dated = DocumentCreate(**(document_data() | {"published_at": "1943-05-01T10:00:00-03:00"}))
    assert dated.published_at == datetime(1943, 5, 1, 13, tzinfo=timezone.utc)
    assert not {"version", "status", "is_active", "actor_id"} & DocumentCreate.model_fields.keys()


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_id", "invalid"),
        ("title", ""),
        ("title", "  "),
        ("title", "x" * 256),
        ("logical_name", ""),
        ("logical_name", "\t"),
        ("logical_name", "x" * 101),
        ("checksum_sha256", "x" * 64),
        ("checksum_sha256", "a" * 63),
        ("checksum_sha256", "a" * 65),
        ("published_at", "2026-01-01T12:00:00"),
    ],
)
def test_invalid_document(field: str, value: str) -> None:
    with pytest.raises(ValidationError):
        DocumentCreate(**(document_data() | {field: value}))


@pytest.mark.parametrize("field", ["source_id", "title", "logical_name", "checksum_sha256"])
def test_required_document_fields(field: str) -> None:
    data = document_data()
    del data[field]
    with pytest.raises(ValidationError):
        DocumentCreate(**data)


def test_responses_serialize_orm_without_internal_state() -> None:
    now = datetime.now(timezone.utc)
    source = Source(id=uuid7(), created_at=now, **source_data())
    result = SourceResponse.model_validate(source).model_dump(mode="json")
    assert result["id"] == str(source.id)
    assert result["created_at"].endswith("Z")
    assert result["description"] is None
    assert "_sa_instance_state" not in result

    document = Document(
        id=uuid7(),
        created_at=now,
        updated_at=now,
        version=1,
        is_active=False,
        status=DocumentStatus.PROCESSING,
        **document_data(),
    )
    result = DocumentResponse.model_validate(document).model_dump(mode="json")
    assert result["source_id"] == str(document.source_id)
    assert result["status"] == "PROCESSING"
    assert result["published_at"] is None
    assert result["updated_at"].endswith("Z")
    assert not {"chunks", "content", "_sa_instance_state"} & result.keys()


def test_status_requires_boolean() -> None:
    assert DocumentStatusUpdate(is_active=False).is_active is False
    with pytest.raises(ValidationError):
        DocumentStatusUpdate()
    with pytest.raises(ValidationError):
        DocumentStatusUpdate(is_active="invalid")
