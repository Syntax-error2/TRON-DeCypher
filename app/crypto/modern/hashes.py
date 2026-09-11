import hashlib
import time

from app.crypto.models import CryptoInput, CryptoResult


class HashAnalysisService:
    """Provides hash identification and generation for common modern formats."""
    
    HASH_LENGTHS = {
        32: ["MD5", "NTLM", "MD4"],
        40: ["SHA1"],
        56: ["SHA224", "SHA3-224"],
        64: ["SHA256", "SHA3-256", "BLAKE2s"],
        96: ["SHA384", "SHA3-384"],
        128: ["SHA512", "SHA3-512", "BLAKE2b"]
    }
    
    def identify(self, crypto_input: CryptoInput) -> CryptoResult:
        """Estimates the type of hash based on string length and format."""
        start_time = time.time()
        
        if isinstance(crypto_input.value, bytes):
            text = crypto_input.value.decode('utf-8', errors='ignore').strip()
        else:
            text = crypto_input.value.strip()
            
        candidates = []
        observations: list[str] = []
        
        # Check standard hex hashes
        import re
        if re.match(r'^[0-9a-fA-F]+$', text):
            length = len(text)
            possible = self.HASH_LENGTHS.get(length, [])
            for p in possible:
                candidates.append({
                    "algorithm": p,
                    "confidence": 0.9 if len(possible) == 1 else 0.8,
                    "reason": f"Hex string of length {length}"
                })
                
        # Check bcrypt
        if re.match(r'^\$2[ayb]\$[0-9]{2}\$[A-Za-z0-9./]{53}$', text):
            candidates.append({
                "algorithm": "bcrypt",
                "confidence": 0.95,
                "reason": "Standard bcrypt modular crypt format"
            })
            
        # Check Argon2
        if text.startswith("$argon2"):
            candidates.append({
                "algorithm": "Argon2",
                "confidence": 0.95,
                "reason": "Argon2 modular crypt format identifier"
            })
            
        candidates.sort(key=lambda x: float(str(x["confidence"])), reverse=True)
        
        return CryptoResult(
            algorithm="Hash Identification",
            operation="detect",
            success=len(candidates) > 0,
            confidence=float(str(candidates[0]["confidence"])) if candidates else 0.0,
            candidates=candidates,
            observations=observations,
            execution_time=time.time()-start_time
        )
        
    def hash_text(self, text: str, algo: str) -> str | None:
        """Generates a standard hash."""
        algo = algo.lower()
        if hasattr(hashlib, algo):
            h = hashlib.new(algo)
            h.update(text.encode('utf-8'))
            return h.hexdigest()
        return None

hash_analysis_service = HashAnalysisService()
