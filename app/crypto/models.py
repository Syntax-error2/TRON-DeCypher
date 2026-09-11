from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def utc_now() -> datetime:
    return datetime.now(UTC)

@dataclass
class CryptoInput:
    """Normalized input for cryptanalysis operations."""
    value: str | bytes
    input_type: str = "text"  # "text", "bytes", "hex", "base64"
    encoding: str = "utf-8"
    artifact_id: str | None = None
    case_id: str | None = None
    
    def get_bytes(self) -> bytes:
        if isinstance(self.value, bytes):
            return self.value
        if self.input_type == "hex":
            try:
                return bytes.fromhex(self.value.strip())
            except ValueError:
                return self.value.encode(self.encoding, errors='ignore')
        import base64
        if self.input_type == "base64":
            try:
                return base64.b64decode(self.value)
            except Exception:
                return self.value.encode(self.encoding, errors='ignore')
        return self.value.encode(self.encoding, errors='ignore')

@dataclass
class CryptoResult:
    """Flexible output for various analytical modules."""
    algorithm: str
    operation: str  # "analyze", "detect", "factor", "crack"
    success: bool
    confidence: float = 0.0
    plaintext: str | bytes | None = None
    candidates: list[dict[str, Any]] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    observations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=utc_now)
