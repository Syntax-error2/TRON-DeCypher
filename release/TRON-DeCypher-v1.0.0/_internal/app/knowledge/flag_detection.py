import re
from dataclasses import dataclass


@dataclass
class FlagCandidate:
    value: str
    pattern: str
    source: str
    offset: int = -1
    confidence: str = "HIGH"

class FlagDetectionService:
    def __init__(self):
        # Default fallback
        self.default_patterns = [r"CTF\{.*?\}", r"TRON\{.*?\}", r"FLAG\{.*?\}"]
        
    def set_patterns(self, patterns: list[str]):
        # Convert literal format TRON{...} to regex if needed
        self.patterns = []
        for p in patterns:
            p_reg = p.replace("{...}", r"\{.*?\}").replace("{}", r"\{.*?\}")
            if not p_reg.endswith("}"):
                p_reg += r".*?\}"
            self.patterns.append(p_reg)

    def detect(self, text: str, source: str) -> list[FlagCandidate]:
        results = []
        patterns_to_use = getattr(self, 'patterns', self.default_patterns)
        
        for pat in patterns_to_use:
            try:
                for match in re.finditer(pat, text, re.IGNORECASE):
                    results.append(FlagCandidate(
                        value=match.group(0),
                        pattern=pat,
                        source=source,
                        offset=match.start(),
                        confidence="HIGH"
                    ))
            except re.error:
                continue
                
        # Deduplicate by value and offset
        unique = {}
        for r in results:
            key = f"{r.value}_{r.offset}"
            unique[key] = r
            
        return list(unique.values())

flag_detection_service = FlagDetectionService()
