from typing import Any

from pydantic import BaseModel

from app.models.artifact import Artifact
from app.models.finding import Finding


class EntropyResult(BaseModel):
    entropy: float
    window: int | None = None
    offset: int | None = None

class StringResult(BaseModel):
    offset: int
    encoding: str
    string: str

class TriageResult(BaseModel):
    """Structured result of the basic triage pipeline."""
    artifact: Artifact
    hashes: dict[str, str] = {}
    file_identification: dict[str, Any] = {}
    strings: list[StringResult] = []
    entropy: EntropyResult | None = None
    findings: list[Finding] = []
    execution_metadata: dict[str, Any] = {}
