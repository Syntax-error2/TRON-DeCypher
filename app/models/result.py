from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)

class Result(BaseModel):
    """Represents the output from an analyzer or tool."""
    id: str
    analyzer: str
    artifact_id: str
    status: str
    output: Any
    created_at: datetime = Field(default_factory=utc_now)
    execution_time: float = 0.0
