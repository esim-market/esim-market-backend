from datetime import UTC, datetime
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING


class DummyDocument(Document):
    """Minimal document used to verify Beanie initialization and connectivity."""

    name: str
    dummy_unique_field: Annotated[
        str,
        Indexed(index_type=ASCENDING, unique=True),
    ]
    dummy_indexed_field: Annotated[
        str,
        Indexed(index_type=ASCENDING),
    ]
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "dummy_documents"
