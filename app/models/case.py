from datetime import UTC, datetime

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)

class Case(BaseModel):
    """Represents a forensic case or CTF workspace."""
    id: str
    name: str
    description: str | None = None
    status: str = "open"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
