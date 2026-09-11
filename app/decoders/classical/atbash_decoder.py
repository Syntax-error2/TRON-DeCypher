from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class AtbashDecoder(DecoderBase):
    name = "Atbash Cipher"
    category = "classical_ciphers"
    description = "Reversible substitution cipher (A=Z, B=Y, etc)."
    expected_params = {}
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        result = []
        for char in text:
            if 'a' <= char <= 'z':
                result.append(chr(ord('z') - (ord(char) - ord('a'))))
            elif 'A' <= char <= 'Z':
                result.append(chr(ord('Z') - (ord(char) - ord('A'))))
            else:
                result.append(char)
                
        decoded = "".join(result)
        return self._create_result(True, output_text=decoded)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text or not any(c.isalpha() for c in text):
            return 0.0, {}
        return 0.05, {"reason": "Possible Atbash"}
