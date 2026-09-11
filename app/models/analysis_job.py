from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel


def utc_now() -> datetime:
    return datetime.now(UTC)

class AnalysisJob(BaseModel):
    """Represents a job for an analyzer to execute."""
    id: str
    analyzer_name: str
    artifact_id: str
    case_id: str
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration: float = 0.0
    result: Any | None = None
    error: str | None = None
