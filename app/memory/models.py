from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryProcess:
    pid: int
    ppid: int
    name: str
    path: str = ""
    start_time: str = ""
    session: str = ""
    architecture: str = ""
    command_line: str = ""

@dataclass
class MemoryNetworkConnection:
    process_name: str
    pid: int
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    state: str
    protocol: str = "TCP"

@dataclass
class MemoryModule:
    process_name: str
    pid: int
    name: str
    path: str = ""
    base_address: str = ""
    size: str = ""

@dataclass
class MemoryHandle:
    pid: int
    handle_value: str
    type: str
    name: str

@dataclass
class MemoryFinding:
    severity: str # INFO, LOW, MEDIUM, HIGH, CRITICAL
    description: str
    source: str

@dataclass
class MemoryAnalysisResult:
    file_path: str = ""
    size_bytes: int = 0
    os_hint: str = "Unknown"
    architecture_hint: str = "Unknown"
    
    processes: list[MemoryProcess] = field(default_factory=list)
    connections: list[MemoryNetworkConnection] = field(default_factory=list)
    modules: list[MemoryModule] = field(default_factory=list)
    handles: list[MemoryHandle] = field(default_factory=list)
    strings: list[dict[str, Any]] = field(default_factory=list)
    findings: list[MemoryFinding] = field(default_factory=list)
    iocs_extracted: int = 0
