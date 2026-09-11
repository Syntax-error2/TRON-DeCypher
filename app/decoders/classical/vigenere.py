from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class VigenereDecoder(DecoderBase):
    name = "Vigenère Cipher"
    category = "classical_ciphers"
    description = "Polyalphabetic substitution cipher using a keyword."
    expected_params = {
        "key": {"type": "str", "default": "KEY", "description": "Keyword"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"}
    }
    
    def _transform(self, text: str, key: str, decrypt: bool) -> str:
        key_chars = [c.upper() for c in key if c.isalpha()]
        if not key_chars:
            return text
            
        result = []
        key_idx = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                k = ord(key_chars[key_idx % len(key_chars)]) - ord('A')
                if decrypt:
                    val = (ord(char) - base - k) % 26
                else:
                    val = (ord(char) - base + k) % 26
                result.append(chr(val + base))
                key_idx += 1
            else:
                result.append(char)
        return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        key = context.get("key", "KEY")
        if not any(c.isalpha() for c in key):
            return self._create_result(False, errors=["Key must contain letters"])
            
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        
        dec = self._transform(text, str(key), decrypt)
        return self._create_result(True, output_text=dec)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text or not any(c.isalpha() for c in text):
            return 0.0, {}
        return 0.05, {"reason": "Possible Vigenère"}
