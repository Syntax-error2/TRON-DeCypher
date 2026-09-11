import re
from typing import Any

from app.crypto.models import CryptoInput, CryptoResult


class CryptoIdentificationService:
    """Heuristics to classify text/bytes as potential encodings or crypto structures."""
    
    def analyze(self, crypto_input: CryptoInput) -> CryptoResult:
        import time
        start_time = time.time()
        
        candidates: list[dict[str, Any]] = []
        observations: list[str] = []
        
        if isinstance(crypto_input.value, bytes):
            text = crypto_input.value.decode('utf-8', errors='ignore')
        else:
            text = crypto_input.value
            
        text = text.strip()
        if not text:
            return CryptoResult("Identification", "detect", False, execution_time=time.time()-start_time)
            
        # Check Base64
        if re.match(r'^[A-Za-z0-9+/]+={0,2}$', text):
            if len(text) % 4 == 0:
                candidates.append({"algorithm": "Base64", "confidence": 0.9, "reason": "Valid characters and length"})
            else:
                candidates.append({"algorithm": "Base64", "confidence": 0.4, "reason": "Valid characters but invalid padding length"})
                
        # Check Hex
        if re.match(r'^([0-9a-fA-F]{2})+$', text):
            candidates.append({"algorithm": "Hex", "confidence": 0.95, "reason": "Even-length hex string"})
        elif re.match(r'^[0-9a-fA-F]+$', text):
            candidates.append({"algorithm": "Hex", "confidence": 0.6, "reason": "Hex characters only but odd length"})
            
        # Check Binary
        if re.match(r'^[01]+$', text):
            if len(text) % 8 == 0:
                candidates.append({"algorithm": "Binary", "confidence": 0.9, "reason": "Binary characters and byte-aligned"})
            else:
                candidates.append({"algorithm": "Binary", "confidence": 0.6, "reason": "Binary characters but not byte-aligned"})
                
        # Check PEM
        if "-----BEGIN" in text and "-----END" in text:
            if "RSA PRIVATE KEY" in text:
                candidates.append({"algorithm": "PEM RSA Private Key", "confidence": 1.0, "reason": "Explicit PEM header"})
            elif "PUBLIC KEY" in text:
                candidates.append({"algorithm": "PEM Public Key", "confidence": 1.0, "reason": "Explicit PEM header"})
            else:
                candidates.append({"algorithm": "PEM Key/Certificate", "confidence": 1.0, "reason": "Explicit PEM header"})
                
        # Check JWT
        if re.match(r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$', text):
            candidates.append({"algorithm": "JWT", "confidence": 0.85, "reason": "Standard 3-part Base64Url format"})
            
        # Check purely alphabetic (Substitution/Caesar/Vigenere candidate)
        if re.match(r'^[A-Za-z\s]+$', text) and len(text) > 10:
            candidates.append({"algorithm": "Substitution/Caesar/Vigenere", "confidence": 0.7, "reason": "Purely alphabetic text"})
            
        # Sort by confidence
        candidates.sort(key=lambda x: x["confidence"], reverse=True)
        
        return CryptoResult(
            algorithm="Identification",
            operation="detect",
            success=len(candidates) > 0,
            confidence=candidates[0]["confidence"] if candidates else 0.0,
            candidates=candidates,
            observations=observations,
            execution_time=time.time() - start_time
        )

crypto_identification_service = CryptoIdentificationService()
