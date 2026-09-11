from dataclasses import dataclass, field
from typing import Any

from PIL import Image


@dataclass
class SymbolBoundingBox:
    x: int
    y: int
    w: int
    h: int
    
    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

@dataclass
class SymbolItem:
    bbox: SymbolBoundingBox
    crop: Image.Image
    symbol_id: str = "" # Matches identical symbols
    confidence: float = 0.0
    
@dataclass
class SymbolProfile:
    id: str
    name: str
    mapping: dict[str, str] = field(default_factory=dict)
    
@dataclass
class SymbolResult:
    detected_symbols: list[SymbolItem] = field(default_factory=list)
    unique_symbols: int = 0
    directions_tested: dict[str, str] = field(default_factory=dict)
    best_candidate: str = ""
    candidates: list[dict[str, Any]] = field(default_factory=list)
    mapping_used: dict[str, str] = field(default_factory=dict)
    profile: str = "Unknown"
    confidence: float = 0.0
