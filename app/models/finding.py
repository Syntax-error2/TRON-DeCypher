from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)

class Finding(BaseModel):
    """Represents a discovered issue or flag."""
    id: str
    case_id: str
    artifact_id: str | None = None
    category: str
    severity: str
    title: str
    description: str
    evidence: Any | None = None
    created_at: datetime = Field(default_factory=utc_now)
