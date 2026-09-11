import re
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class PolybiusDecoder(DecoderBase):
    name = "Polybius Square"
    category = "classical_ciphers"
    description = "Substitution cipher where each letter is replaced by its coordinates in a grid."
    expected_params = {
        "mode": {"type": "str", "default": "decode", "description": "encode or decode"},
        "replace": {"type": "str", "default": "J=I", "description": "J=I or I=J"}
    }
    
    def _create_matrix(self, replace_char: str, with_char: str) -> list[list[str]]:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".replace(replace_char, "")
        matrix = []
        for i in range(5):
            matrix.append(list(alphabet[i*5:(i+1)*5]))
        return matrix
        
    def _find_pos(self, matrix: list[list[str]], char: str) -> tuple[int, int] | None:
        for r in range(5):
            for c in range(5):
                if matrix[r][c] == char:
                    return r, c
        return None

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decode")
        decrypt = mode.lower() != "encode"
        
        replace = context.get("replace", "J=I").upper()
        if replace == "I=J":
            replace_char, with_char = "I", "J"
        else:
            replace_char, with_char = "J", "I"
            
        matrix = self._create_matrix(replace_char, with_char)
        
        if decrypt:
            nums = re.findall(r'[1-5]', text)
            if len(nums) % 2 != 0:
                return self._create_result(False, errors=["Odd number of coordinate digits found."])
            
            result = []
            for i in range(0, len(nums), 2):
                r = int(nums[i]) - 1
                c = int(nums[i+1]) - 1
                result.append(matrix[r][c])
            return self._create_result(True, output_text="".join(result))
        else:
            result = []
            for char in text.upper():
                if char.isalpha():
                    if char == replace_char:
                        char = with_char
                    pos = self._find_pos(matrix, char)
                    if pos:
                        result.append(f"{pos[0]+1}{pos[1]+1}")
            return self._create_result(True, output_text=" ".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text:
            return 0.0, {}
        nums = re.findall(r'\d', text)
        if nums and all(n in "12345" for n in nums):
            if len(nums) % 2 == 0 and len(nums) > 0:
                return 0.4, {"reason": "Matches 1-5 digit coordinate pattern"}
        return 0.05, {"reason": "Possible Polybius"}

class A1Z26Decoder(DecoderBase):
    name = "A1Z26 Cipher"
    category = "classical_ciphers"
    description = "Substitution cipher where A=1, B=2 ... Z=26."
    expected_params = {
        "mode": {"type": "str", "default": "decode", "description": "encode or decode"}
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decode")
        decrypt = mode.lower() != "encode"
        
        if decrypt:
            nums = re.findall(r'\d+', text)
            result = []
            for n in nums:
                val = int(n)
                if 1 <= val <= 26:
                    result.append(chr(val - 1 + ord('A')))
            return self._create_result(True, output_text="".join(result))
        else:
            result = []
            for char in text.upper():
                if char.isalpha():
                    result.append(str(ord(char) - ord('A') + 1))
            return self._create_result(True, output_text=" ".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text:
            return 0.0, {}
        nums = re.findall(r'\d+', text)
        if nums and all(1 <= int(n) <= 26 for n in nums):
            return 0.5, {"reason": "Matches 1-26 digit pattern"}
        return 0.05, {}

class TapCodeDecoder(DecoderBase):
    name = "Tap Code"
    category = "classical_ciphers"
    description = "Prisoner's dot/tap cipher similar to Polybius (C/K merged)."
    expected_params = {
        "mode": {"type": "str", "default": "decode", "description": "encode or decode"}
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decode")
        decrypt = mode.lower() != "encode"
        
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".replace("K", "")
        matrix = []
        for i in range(5):
            matrix.append(list(alphabet[i*5:(i+1)*5]))
            
        if decrypt:
            # Match groups of dots/dashes or numbers. We'll extract digits 1-5 or count consecutive dots.
            if "." in text or "-" in text:
                parts = re.findall(r'[\.\-]+', text)
                nums = [len(p) for p in parts if len(p) <= 5]
            else:
                nums = [int(n) for n in re.findall(r'[1-5]', text)]
                
            if len(nums) % 2 != 0:
                return self._create_result(False, errors=["Odd number of taps/digits found."])
                
            result = []
            for i in range(0, len(nums), 2):
                r = nums[i] - 1
                c = nums[i+1] - 1
                result.append(matrix[r][c])
            return self._create_result(True, output_text="".join(result))
        else:
            result = []
            for char in text.upper():
                if char.isalpha():
                    if char == "K":
                        char = "C"
                    for r in range(5):
                        for c in range(5):
                            if matrix[r][c] == char:
                                result.append(f"{r+1}-{c+1}")
            return self._create_result(True, output_text=" ".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {"reason": "Possible Tap Code"}

