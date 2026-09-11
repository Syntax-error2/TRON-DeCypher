from typing import Any

from pydantic import BaseModel


class StegoDetectionResult(BaseModel):
    analyzer: str
    confidence: float
    reason: str
    metadata: dict[str, Any] = {}

class StegoExtractionResult(BaseModel):
    analyzer: str
    channel: str
    extracted_text: str | None = None
    extracted_bytes: bytes | None = None
    metadata: dict[str, Any] = {}
