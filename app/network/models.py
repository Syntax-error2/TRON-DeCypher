from dataclasses import dataclass, field


@dataclass
class PacketSummary:
    packet_number: int
    timestamp: float
    length: int
    src_mac: str | None = None
    dst_mac: str | None = None
    src_ip: str | None = None
    dst_ip: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    protocol: str = "Unknown"
    info: str = ""

@dataclass
class Conversation:
    src_ip: str
    dst_ip: str
    src_port: int | None
    dst_port: int | None
    protocol: str
    packet_count: int = 0
    bytes_transferred: int = 0
    first_seen: float = 0.0
    last_seen: float = 0.0

@dataclass
class DNSQuery:
    timestamp: float
    client: str
    server: str
    query: str
    qtype: str
    answers: list[str] = field(default_factory=list)
    
@dataclass
class HTTPRequest:
    timestamp: float
    client: str
    server: str
    method: str
    host: str
    uri: str
    status_code: int | None = None
    content_type: str | None = None

@dataclass
class PcapStatistics:
    total_packets: int = 0
    total_bytes: int = 0
    first_timestamp: float = 0.0
    last_timestamp: float = 0.0
    protocols: dict[str, int] = field(default_factory=dict)
    top_src_ips: dict[str, int] = field(default_factory=dict)
    top_dst_ips: dict[str, int] = field(default_factory=dict)
    conversations: list[Conversation] = field(default_factory=list)
    dns_queries: list[DNSQuery] = field(default_factory=list)
    http_requests: list[HTTPRequest] = field(default_factory=list)
