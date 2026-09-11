from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)

class DecoderInput(BaseModel):
    """Normalized input for decoders."""
    text: str | None = None
    data: bytes | None = None
    source_type: str = "text" # "text", "bytes", "artifact"
    artifact_id: str | None = None
    encoding: str = "utf-8"

class DecoderResult(BaseModel):
    """Normalized output from decoders."""
    success: bool
    decoder: str
    output_text: str | None = None
    output_data: bytes | None = None
    output_type: str = "text"
    confidence: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0

class TransformationStep(BaseModel):
    id: str
    decoder_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    result: DecoderResult | None = None
    timestamp: datetime = Field(default_factory=utc_now)

class TransformationPipeline(BaseModel):
    id: str
    name: str = "Unnamed Pipeline"
    steps: list[TransformationStep] = Field(default_factory=list)

class HashResult(BaseModel):
    algorithm: str
    digest: str
    input_type: str = "text"
    input_size: int
    source_reference: str | None = None
    execution_time: float = 0.0

class HashCandidate(BaseModel):
    algorithm: str
    confidence: float
    length_match: bool
    charset_match: bool
    prefix_match: bool
    reasons: list[str] = Field(default_factory=list)
