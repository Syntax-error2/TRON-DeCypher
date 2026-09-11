from dataclasses import dataclass, field
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)

@dataclass
class HTTPRequest:
    method: str = "GET"
    url: str = ""
    scheme: str = "http"
    host: str = ""
    port: int = 80
    path: str = "/"
    query: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    body: str | bytes = ""
    content_type: str = ""
    timestamp: datetime = field(default_factory=utc_now)
    source: str = "manual"  # e.g., "pcap", "manual", "har"

@dataclass
class HTTPResponse:
    status_code: int = 0
    reason: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    cookies: dict[str, str] = field(default_factory=dict)
    body: str | bytes = ""
    content_type: str = ""
    content_length: int = 0
    timestamp: datetime = field(default_factory=utc_now)
    url: str = ""
    
    @property
    def is_html(self) -> bool:
        return "text/html" in self.content_type.lower()
        
    @property
    def is_json(self) -> bool:
        return "application/json" in self.content_type.lower()
        
    def get_text(self) -> str:
        if isinstance(self.body, str):
            return self.body
        return self.body.decode('utf-8', errors='ignore')

@dataclass
class HTTPTransaction:
    request: HTTPRequest
    response: HTTPResponse | None = None
    duration: float = 0.0
    redirects: list[str] = field(default_factory=list)
    source: str = "manual"
    id: str = ""
