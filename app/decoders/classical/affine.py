import math
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class AffineDecoder(DecoderBase):
    name = "Affine Cipher"
    category = "classical_ciphers"
    description = "E(x) = (a*x + b) mod 26"
    expected_params = {
        "a": {"type": "int", "default": 5, "description": "Multiplier (coprime to 26)"},
        "b": {"type": "int", "default": 8, "description": "Shift (0-25)"},
        "auto_crack": {"type": "bool", "default": False, "description": "Try all valid keys"}
    }
    
    def _mod_inverse(self, a: int, m: int) -> int | None:
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None

    def _decode_affine(self, text: str, a: int, b: int) -> str | None:
        a_inv = self._mod_inverse(a, 26)
        if a_inv is None:
            return None
            
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((a_inv * (ord(char) - base - b)) % 26 + base))
            else:
                result.append(char)
        return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        auto_crack = context.get("auto_crack", False)
        
        valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
        
        if auto_crack:
            best_score = -1.0
            best_text = ""
            best_a = 1
            best_b = 0
            
            candidates = []
            for a in valid_a:
                for b in range(26):
                    cand = self._decode_affine(text, a, b)
                    if cand:
                        score = text_analysis_service.score_english(cand)
                        candidates.append((score, a, b, cand))
                        if score > best_score:
                            best_score = score
                            best_text = cand
                            best_a = a
                            best_b = b
                            
            candidates.sort(reverse=True, key=lambda x: x[0])
            top_cands = [{"score": c[0], "parameters": f"a={c[1]}, b={c[2]}", "candidate": c[3]} for c in candidates[:5]]
            
            return self._create_result(
                True, 
                output_text=best_text, 
                metadata={"best_a": best_a, "best_b": best_b, "candidates": top_cands, "auto_crack": True}
            )
        else:
            try:
                a = int(context.get("a", 5))
                b = int(context.get("b", 8))
            except ValueError:
                return self._create_result(False, errors=["Invalid parameters for a or b"])
                
            if math.gcd(a, 26) != 1:
                return self._create_result(False, errors=[f"Parameter 'a' ({a}) must be coprime to 26."])
                
            dec = self._decode_affine(text, a, b)
            if dec is None:
                return self._create_result(False, errors=["Could not compute modular inverse."])
                
            return self._create_result(True, output_text=dec)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text or not any(c.isalpha() for c in text):
            return 0.0, {}
        # We don't brute force affine for detection as it's slightly heavier, just return low prob
        return 0.05, {"reason": "Possible Affine"}
