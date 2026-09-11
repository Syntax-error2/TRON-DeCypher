from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class BifidDecoder(DecoderBase):
    name = "Bifid Cipher"
    category = "classical_ciphers"
    description = "Combines Polybius square with transposition."
    expected_params = {
        "key": {"type": "str", "default": "", "description": "Keyword"},
        "period": {"type": "int", "default": 5, "description": "Period/Block size"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"}
    }
    
    def _create_matrix(self, key: str) -> list[list[str]]:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".replace("J", "")
        key = key.upper().replace("J", "I")
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

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        key = context.get("key", "")
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        try:
            period = int(context.get("period", 5))
        except ValueError:
            return self._create_result(False, errors=["Period must be an integer"])
            
        matrix = self._create_matrix(str(key))
        clean_text = "".join([c.upper() for c in text if c.isalpha()]).replace("J", "I")
        
        result = []
        for i in range(0, len(clean_text), period):
            block = clean_text[i:i+period]
            if decrypt:
                coords = []
                for char in block:
                    r, c = self._find_pos(matrix, char)
                    coords.extend([r, c])
                
                half = len(block)
                row_coords = coords[:half]
                col_coords = coords[half:]
                
                for j in range(half):
                    result.append(matrix[row_coords[j]][col_coords[j]])
            else:
                row_coords = []
                col_coords = []
                for char in block:
                    r, c = self._find_pos(matrix, char)
                    row_coords.append(r)
                    col_coords.append(c)
                
                coords = row_coords + col_coords
                for j in range(0, len(coords), 2):
                    result.append(matrix[coords[j]][coords[j+1]])
                    
        return self._create_result(True, output_text="".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {"reason": "Possible Bifid"}

class TrifidDecoder(DecoderBase):
    name = "Trifid Cipher"
    category = "classical_ciphers"
    description = "Fractional cipher using a 3x3x3 grid."
    expected_params = {
        "key": {"type": "str", "default": "", "description": "Keyword"},
        "period": {"type": "int", "default": 5, "description": "Period/Block size"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"}
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        # Simplified trifid stub. Implementing full trifid correctly takes a lot of matrix logic.
        # But we must support it as requested.
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        key = str(context.get("key", ""))
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        try:
            period = int(context.get("period", 5))
        except ValueError:
            return self._create_result(False, errors=["Period must be an integer"])
            
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ+" # 27 chars
        key_str = ""
        for char in key.upper() + alphabet:
            if char not in key_str and char in alphabet:
                key_str += char
                
        def get_pos(c):
            idx = key_str.index(c)
            return idx // 9, (idx % 9) // 3, idx % 3
            
        clean_text = "".join([c.upper() for c in text if c.upper() in alphabet])
        result = []
        for i in range(0, len(clean_text), period):
            block = clean_text[i:i+period]
            if decrypt:
                coords = []
                for char in block:
                    coords.extend(get_pos(char))
                
                third = len(block)
                c1 = coords[:third]
                c2 = coords[third:2*third]
                c3 = coords[2*third:]
                
                for j in range(third):
                    idx = c1[j] * 9 + c2[j] * 3 + c3[j]
                    result.append(key_str[idx])
            else:
                c1, c2, c3 = [], [], []
                for char in block:
                    p1, p2, p3 = get_pos(char)
                    c1.append(p1)
                    c2.append(p2)
                    c3.append(p3)
                
                coords = c1 + c2 + c3
                for j in range(0, len(coords), 3):
                    idx = coords[j] * 9 + coords[j+1] * 3 + coords[j+2]
                    result.append(key_str[idx])
                    
        return self._create_result(True, output_text="".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {}
