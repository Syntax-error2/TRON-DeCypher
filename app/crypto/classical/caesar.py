import string
import time
from typing import Any

from app.crypto.models import CryptoInput, CryptoResult


class CaesarAnalyzer:
    """Brute force Caesar cipher shifts and score candidates."""
    
    # English bigram/trigram or simple frequency scoring could be used.
    # For now, simple frequency distance to English.
    ENGLISH_FREQ = {
        'E': 13.0, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7, 'S': 6.3,
        'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4,
        'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5, 'V': 0.98,
        'K': 0.77, 'J': 0.15, 'X': 0.15, 'Q': 0.09, 'Z': 0.07
    }
    
    def analyze(self, crypto_input: CryptoInput) -> CryptoResult:
        start_time = time.time()
        
        if isinstance(crypto_input.value, bytes):
            text = crypto_input.value.decode('utf-8', errors='ignore')
        else:
            text = crypto_input.value
            
        candidates: list[dict[str, Any]] = []
        
        for shift in range(26):
            shifted = self._shift_text(text, shift)
            score = self._score_english(shifted)
            candidates.append({
                "shift": shift,
                "score": score,
                "plaintext": shifted,
                "preview": shifted[:100] + ("..." if len(shifted) > 100 else "")
            })
            
        # Sort by score descending
        candidates.sort(key=lambda x: float(str(x["score"])), reverse=True)
        
        # High confidence if top score is significantly better
        confidence = 0.0
        if float(str(candidates[0]["score"])) > 50.0 and (float(str(candidates[0]["score"])) - float(str(candidates[1]["score"]))) > 20.0:
            confidence = 0.9
            
        return CryptoResult(
            algorithm="Caesar",
            operation="crack",
            success=True,
            confidence=confidence,
            candidates=candidates,
            observations=[f"Top shift is {candidates[0]['shift']} with score {float(str(candidates[0]['score'])):.2f}"],
            execution_time=time.time()-start_time
        )
        
    def _shift_text(self, text: str, shift: int) -> str:
        result = []
        for char in text:
            if char.isupper():
                result.append(chr(((ord(char) - 65 + shift) % 26) + 65))
            elif char.islower():
                result.append(chr(((ord(char) - 97 + shift) % 26) + 97))
            else:
                result.append(char)
        return ''.join(result)
        
    def _score_english(self, text: str) -> float:
        """Simple frequency scoring."""
        letters = [c.upper() for c in text if c.upper() in string.ascii_uppercase]
        if not letters:
            return 0.0
            
        from collections import Counter
        counts = Counter(letters)
        N = len(letters)
        
        score = 0.0
        for char, count in counts.items():
            freq = (count / N) * 100
            expected = self.ENGLISH_FREQ.get(char, 0)
            # Penalize deviation
            score += 100.0 - abs(freq - expected)*10
            
        return score / len(counts) if counts else 0.0

caesar_analyzer = CaesarAnalyzer()
