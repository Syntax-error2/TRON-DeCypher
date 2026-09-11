from dataclasses import dataclass, field
from typing import Any


@dataclass
class BinarySection:
    name: str
    virtual_address: int
    virtual_size: int
    raw_size: int
    offset: int
    entropy: float = 0.0
    permissions: str = ""
    flags: list[str] = field(default_factory=list)

@dataclass
class ImportExport:
    is_import: bool
    library: str
    function: str
    address: int = 0
    ordinal: int = 0
    category: str = "Unknown"

@dataclass
class DisassembledInstruction:
    address: int
    bytes_hex: str
    mnemonic: str
    operands: str

@dataclass
class ProtectionStatus:
    nx: str = "Unknown"
    pie: str = "Unknown"
    aslr: str = "Unknown"
    relro: str = "Unknown"
    canary: str = "Unknown"
    signed: str = "Unknown"

@dataclass
class BinaryAnalysisResult:
    format: str = "Unknown"
    architecture: str = "Unknown"
    bitness: str = "Unknown"
    endianness: str = "Unknown"
    entry_point: int = 0
    compiler: str = "Unknown"
    
    sections: list[BinarySection] = field(default_factory=list)
    imports: list[ImportExport] = field(default_factory=list)
    exports: list[ImportExport] = field(default_factory=list)
    strings: list[dict[str, Any]] = field(default_factory=list)
    symbols: list[dict[str, Any]] = field(default_factory=list)
    protections: ProtectionStatus = field(default_factory=ProtectionStatus)
    
    findings: list[str] = field(default_factory=list)
    entropy: float = 0.0
    is_packed_hint: bool = False
    
    file_path: str = ""
