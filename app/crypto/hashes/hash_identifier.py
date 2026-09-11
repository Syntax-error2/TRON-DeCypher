import re
from typing import NamedTuple

from app.crypto.hashes.hash_formats import hash_format_registry


class HashIdentificationCandidate(NamedTuple):
    algorithm: str
    confidence: float
    reasons: list[str]
    is_structured: bool

class HashIdentifier:
    def __init__(self) -> None:
        self.hex_regex = re.compile(r"^[0-9a-fA-F]+$")

    def identify(self, text: str) -> list[HashIdentificationCandidate]:
        text = text.strip()
        candidates = []
        
        # 1. Check for structured hashes (prefix matches)
        for fmt in hash_format_registry.get_all():
            if fmt.is_structured:
                for prefix in fmt.prefix_patterns:
                    if text.startswith(prefix):
                        candidates.append(HashIdentificationCandidate(
                            algorithm=fmt.name,
                            confidence=0.95,
                            reasons=[f"Starts with known structured prefix: {prefix}", f"Matches {fmt.display_name} format"],
                            is_structured=True
                        ))
        
        if candidates:
            # If we found structured hashes, prioritize them heavily.
            candidates.sort(key=lambda x: x.confidence, reverse=True)
            return candidates

        # 2. Check for generic hex hashes
        if self.hex_regex.match(text):
            length = len(text)
            
            # Map length to possibilities
            length_map = {
                32: ["md5", "md4", "ntlm", "lm"],
                40: ["sha1", "ripemd160"],
                56: ["sha224", "sha512-224", "sha3-224"],
                64: ["sha256", "sha512-256", "sha3-256", "blake2s"],
                96: ["sha384", "sha3-384"],
                128: ["sha512", "sha3-512", "blake2b"]
            }
            
            possible = length_map.get(length, [])
            for algo in possible:
                fmt: HashFormat | None = hash_format_registry.get(algo)
                if fmt:
                    candidates.append(HashIdentificationCandidate(
                        algorithm=fmt.name,
                        confidence=0.90 if algo in ["md5", "sha1", "sha256", "sha512"] else 0.70,
                        reasons=[f"{length} hexadecimal characters", "100% alphabet match", f"Matches {fmt.display_name} digest length"],
                        is_structured=False
                    ))

        candidates.sort(key=lambda x: x.confidence, reverse=True)
        return candidates

hash_identifier = HashIdentifier()
