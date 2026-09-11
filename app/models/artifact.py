from datetime import UTC, datetime

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)

class Artifact(BaseModel):
    """Represents a file or data artifact within a case."""
    id: str
    case_id: str
    filename: str
    original_path: str
    stored_path: str
    size: int
    mime_type: str = "application/octet-stream"
    extension: str | None = None
    sha256: str | None = None
    md5: str | None = None
    parent_artifact_id: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    modified_at: datetime = Field(default_factory=utc_now)
    imported_at: datetime = Field(default_factory=utc_now)
