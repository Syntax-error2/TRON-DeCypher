from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class PlayfairDecoder(DecoderBase):
    name = "Playfair Cipher"
    category = "classical_ciphers"
    description = "Digraphic substitution cipher using a 5x5 matrix."
    expected_params = {
        "key": {"type": "str", "default": "KEY", "description": "Keyword"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"},
        "replace": {"type": "str", "default": "J=I", "description": "J=I or I=J"}
    }
    
    def _create_matrix(self, key: str, replace_char: str, with_char: str) -> list[list[str]]:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".replace(replace_char, "")
        key = key.upper().replace(replace_char, with_char)
        
        matrix_string = ""
        for char in key + alphabet:
            if char.isalpha() and char not in matrix_string:
                matrix_string += char
                
        matrix = []
        for i in range(5):
            matrix.append(list(matrix_string[i*5:(i+1)*5]))
        return matrix
        
    def _find_pos(self, matrix: list[list[str]], char: str) -> tuple[int, int]:
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char:
                    return r, c
        return 0, 0

    def _transform(self, text: str, key: str, decrypt: bool, replace_char: str, with_char: str) -> str:
        matrix = self._create_matrix(key, replace_char, with_char)
        
        # Prepare text
        text_clean = "".join([c.upper() for c in text if c.isalpha()]).replace(replace_char, with_char)
        
        if not decrypt:
            # Insert X between duplicate letters in digraphs
            i = 0
            while i < len(text_clean) - 1:
                if text_clean[i] == text_clean[i+1]:
                    text_clean = text_clean[:i+1] + "X" + text_clean[i+1:]
                i += 2
            if len(text_clean) % 2 != 0:
                text_clean += "X"
        else:
            if len(text_clean) % 2 != 0:
                # If decrypting and odd length, append X just to not crash, though it's invalid
                text_clean += "X"
                
        result = []
        for i in range(0, len(text_clean), 2):
            char1 = text_clean[i]
            char2 = text_clean[i+1]
            
            r1, c1 = self._find_pos(matrix, char1)
            r2, c2 = self._find_pos(matrix, char2)
            
            if r1 == r2:
                shift = -1 if decrypt else 1
                result.append(matrix[r1][(c1 + shift) % 5])
                result.append(matrix[r2][(c2 + shift) % 5])
            elif c1 == c2:
                shift = -1 if decrypt else 1
                result.append(matrix[(r1 + shift) % 5][c1])
                result.append(matrix[(r2 + shift) % 5][c2])
            else:
                result.append(matrix[r1][c2])
                result.append(matrix[r2][c1])
                
        # Reconstruct with punctuation? Playfair destroys punctuation usually.
        # But we can try to inject it back if we assume 1:1 mapping (which isn't true due to X insertions).
        # We will just return the raw decrypted text.
        return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        key = context.get("key", "KEY")
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        
        replace = context.get("replace", "J=I").upper()
        if replace == "I=J":
            replace_char, with_char = "I", "J"
        else:
            replace_char, with_char = "J", "I"
            
        dec = self._transform(text, str(key), decrypt, replace_char, with_char)
        
        matrix = self._create_matrix(str(key), replace_char, with_char)
        mat_str = "\n".join([" ".join(row) for row in matrix])
        
        return self._create_result(True, output_text=dec, metadata={"matrix": mat_str})

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text or not any(c.isalpha() for c in text):
            return 0.0, {}
        # Playfair ciphertext often has no J's (or I's) and even length
        alpha_text = [c.upper() for c in text if c.isalpha()]
        if len(alpha_text) % 2 == 0 and len(alpha_text) > 0:
            if 'J' not in alpha_text:
                return 0.15, {"reason": "Even length, no J"}
        return 0.05, {"reason": "Possible Playfair"}
