from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class RotDecoder(DecoderBase):
    name = "ROT"
    category = "classical_ciphers"
    description = "Decodes ROT13, ROT47, and custom ROT-N shifts."
    expected_params = {
        "variant": {"type": "str", "default": "rot13", "description": "rot13, rot47, or rot_n"},
        "n": {"type": "int", "default": 13, "description": "Shift amount for rot_n"}
    }
    
    def _rot_alpha(self, text: str, shift: int) -> str:
        result = []
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result.append(chr(((ord(char) - base + shift) % 26) + base))
            else:
                result.append(char)
        return "".join(result)
        
    def _rot47(self, text: str) -> str:
        result = []
        for char in text:
            val = ord(char)
            if 33 <= val <= 126:
                result.append(chr(33 + ((val - 33 + 47) % 94)))
            else:
                result.append(char)
        return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        variant = context.get("variant", "rot13").lower()
        
        if variant == "rot13":
            decoded = self._rot_alpha(text, 13)
        elif variant == "rot47":
            decoded = self._rot47(text)
        elif variant == "rot_n":
            try:
                n = int(context.get("n", 13))
            except ValueError:
                return self._create_result(False, errors=["Parameter 'n' must be an integer."])
            decoded = self._rot_alpha(text, n)
        else:
            return self._create_result(False, errors=[f"Unsupported variant: {variant}"])
            
        return self._create_result(True, output_text=decoded)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text:
            return 0.0, {}
        # In phase 14 we will handle flag detection wrapper extraction externally.
        # So we just return low confidence here, unless we auto-crack.
        return 0.05, {"reason": "Possible ROT cipher"}
