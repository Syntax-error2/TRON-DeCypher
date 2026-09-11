import os

from app.memory.models import MemoryAnalysisResult


class MemoryIdentificationAnalyzer:
    """Statically identifies memory image metadata offline."""
    
    def analyze(self, filepath: str, result: MemoryAnalysisResult) -> None:
        if not os.path.exists(filepath):
            return
            
        result.size_bytes = os.path.getsize(filepath)
        
        # Simple static heuristics (magic bytes check)
        with open(filepath, 'rb') as f:
            header = f.read(4096)
            
        if b"PAGE" in header[:4]:
            result.os_hint = "Windows"
            result.architecture_hint = "x64/x86 (Crash Dump)"
        elif b"RSD PTR " in header:
            result.os_hint = "Windows"
            result.architecture_hint = "x64/x86 (Raw Memory)"
        elif header.startswith(b"\x7fELF"):
            result.os_hint = "Linux"
            result.architecture_hint = "x64/x86 (ELF Core Dump)"
        else:
            result.os_hint = "Unknown (Raw Image?)"
            result.architecture_hint = "Unknown"

memory_identification_analyzer = MemoryIdentificationAnalyzer()
