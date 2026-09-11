from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class CaesarDecoder(DecoderBase):
    name = "Caesar Cipher"
    category = "classical_ciphers"
    description = "Shift letters by a fixed amount."
    expected_params = {
        "shift": {"type": "int", "default": 3, "description": "Shift amount (0-25)"},
        "auto_crack": {"type": "bool", "default": False, "description": "Try all shifts automatically"}
    }

    def _shift_text(self, text: str, shift: int) -> str:
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr((ord(char) - base - shift) % 26 + base))
            else:
                result.append(char)
        return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        auto_crack = context.get("auto_crack", False)
        
        if auto_crack:
            best_score = -1.0
            best_text = ""
            best_shift = 0
            
            candidates = []
            for s in range(26):
                cand = self._shift_text(text, s)
                score = text_analysis_service.score_english(cand)
                candidates.append((score, s, cand))
                if score > best_score:
                    best_score = score
                    best_text = cand
                    best_shift = s
                    
            # We can include candidates in metadata
            candidates.sort(reverse=True, key=lambda x: x[0])
            top_cands = [{"score": c[0], "parameters": f"Shift: {c[1]}", "candidate": c[2]} for c in candidates[:5]]
            return self._create_result(
                True, 
                output_text=best_text, 
                metadata={"best_shift": best_shift, "candidates": top_cands, "auto_crack": True}
            )
        else:
            shift = int(context.get("shift", 3))
            dec = self._shift_text(text, shift)
            return self._create_result(True, output_text=dec)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text or not any(c.isalpha() for c in text):
            return 0.0, {}
            
        # Quick auto-crack to see if any shift yields good English
        best_score = 0.0
        for s in range(1, 26):
            cand = self._shift_text(text, s)
            score = text_analysis_service.score_english(cand)
            best_score = max(best_score, score)
                
        if best_score > 0.85:
            return 0.6, {"reason": "Caesar shift produces likely English"}
        return 0.1, {"reason": "Possible Caesar"}

