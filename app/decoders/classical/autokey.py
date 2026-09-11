from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class AutokeyDecoder(DecoderBase):
    name = "Autokey Cipher"
    category = "classical_ciphers"
    description = "Vigenère variant where the key is extended with the plaintext or ciphertext."
    expected_params = {
        "key": {"type": "str", "default": "KEY", "description": "Primer Keyword"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"},
        "key_source": {"type": "str", "default": "plaintext", "description": "plaintext or ciphertext autokey"}
    }
    
    def _transform(self, text: str, primer: str, decrypt: bool, use_plaintext: bool) -> str:
        key_stream = [c.upper() for c in primer if c.isalpha()]
        if not key_stream:
            return text
            
        result = []
        key_idx = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                k = ord(key_stream[key_idx]) - ord('A')
                
                if decrypt:
                    val = (ord(char) - base - k) % 26
                else:
                    val = (ord(char) - base + k) % 26
                    
                pt_char = chr(val + base)
                result.append(pt_char)
                
                if use_plaintext:
                    if decrypt:
                        key_stream.append(pt_char.upper())
                    else:
                        key_stream.append(pt_char.upper()) # In plaintext autokey encrypt, append plaintext
                else:
                    if decrypt:
                        key_stream.append(char.upper()) # In ciphertext autokey, append ciphertext
                    else:
                        key_stream.append(char.upper()) 
                
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
        
        key_source = context.get("key_source", "plaintext")
        use_plaintext = key_source.lower() != "ciphertext"
        
        dec = self._transform(text, str(key), decrypt, use_plaintext)
        return self._create_result(True, output_text=dec)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text or not any(c.isalpha() for c in text):
            return 0.0, {}
        return 0.05, {"reason": "Possible Autokey"}
