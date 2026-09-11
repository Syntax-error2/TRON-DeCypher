from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)

class IOCType(str, Enum):
    IPV4 = "IPV4"
    IPV6 = "IPV6"
    DOMAIN = "DOMAIN"
    URL = "URL"
    EMAIL = "EMAIL"
    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    SHA512 = "SHA512"
    MAC = "MAC"

class IOCOccurrence(BaseModel):
    id: str
    ioc_id: str
    source_artifact_id: str | None = None
    source_result_id: str | None = None
    source_location: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)

class IntelResult(BaseModel):
    id: str
    ioc_id: str
    provider: str
    response_summary: str
    retrieved_at: datetime = Field(default_factory=utc_now)
    expiry: datetime | None = None

class IOC(BaseModel):
    id: str
    case_id: str
    ioc_type: IOCType
    value: str
    normalized_value: str
    first_seen: datetime = Field(default_factory=utc_now)
    last_seen: datetime = Field(default_factory=utc_now)
    
    # In-memory fields for display
    occurrences: list[IOCOccurrence] = Field(default_factory=list)
    intel_results: list[IntelResult] = Field(default_factory=list)
    confidence: str | None = None
    tags: list[str] = Field(default_factory=list)
