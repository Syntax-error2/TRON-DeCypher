from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class KeyboardShiftDecoder(DecoderBase):
    name = "Keyboard Shift"
    category = "classical_ciphers"
    description = "Translates text shifted left/right on a QWERTY keyboard."
    expected_params = {
        "shift": {"type": "str", "default": "left", "description": "left or right"}
    }
    
    QWERTY_ROWS = [
        "1234567890-=",
        "qwertyuiop[]\\",
        "asdfghjkl;'",
        "zxcvbnm,./"
    ]
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        shift_dir = context.get("shift", "left").lower()
        offset = -1 if shift_dir == "left" else 1
        
        result = []
        for char in text:
            is_upper = char.isupper()
            c = char.lower()
            
            shifted = False
            for row in self.QWERTY_ROWS:
                if c in row:
                    idx = row.index(c)
                    new_idx = (idx + offset) % len(row)
                    new_char = row[new_idx]
                    result.append(new_char.upper() if is_upper else new_char)
                    shifted = True
                    break
                    
            if not shifted:
                result.append(char)
                
        return self._create_result(True, output_text="".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {"reason": "Possible Keyboard Shift"}
