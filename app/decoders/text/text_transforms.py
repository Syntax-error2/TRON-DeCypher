import re
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class ReverseDecoder(DecoderBase):
    name = "Reverse"
    category = "text"
    reversible = True
    input_types = ["text", "bytes"]
    output_types = ["text", "bytes"]
    description = "Reverses the input string or bytes."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if input_data.text:
            return self._create_result(True, output_text=input_data.text[::-1])
        if input_data.data:
            return self._create_result(True, output_data=input_data.data[::-1])
        return self._create_result(False, errors=["Empty input"])
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.0, {}

class WhitespaceNormalizationDecoder(DecoderBase):
    name = "Whitespace Normalization"
    category = "text"
    reversible = False
    input_types = ["text"]
    output_types = ["text"]
    description = "Removes excess whitespace."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if not input_data.text: return self._create_result(False, errors=["Empty text"])
        out = re.sub(r'\s+', ' ', input_data.text).strip()
        return self._create_result(True, output_text=out)
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.0, {}

class BaconDecoder(DecoderBase):
    name = "Bacon Cipher"
    category = "classical"
    reversible = True
    input_types = ["text"]
    output_types = ["text"]
    description = "Decodes Bacon's cipher (A/B)."
    
    _bacon_dict = {
        'A': 'aaaaa', 'B': 'aaaab', 'C': 'aaaba', 'D': 'aaabb', 'E': 'aabaa',
        'F': 'aabab', 'G': 'aabba', 'H': 'aabbb', 'I': 'abaaa', 'J': 'abaab',
        'K': 'ababa', 'L': 'ababb', 'M': 'abbaa', 'N': 'abbab', 'O': 'abbba',
        'P': 'abbbb', 'Q': 'baaaa', 'R': 'baaab', 'S': 'baaba', 'T': 'baabb',
        'U': 'babaa', 'V': 'babab', 'W': 'babba', 'X': 'babbb', 'Y': 'bbaaa', 'Z': 'bbaab'
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if not input_data.text: return self._create_result(False, errors=["Empty text"])
        mode = context.get("mode", "decode")
        
        if mode == "decode":
            # Clean non A/B chars
            cleaned = re.sub(r'[^a-zA-Z]', '', input_data.text).lower()
            # Map standard to A/B
            # If it's mostly two chars, map them to a/b
            chars = sorted(list(set(cleaned)))
            if len(chars) > 2:
                return self._create_result(False, errors=["Input contains more than 2 distinct characters."])
            
            if not all(c in ('a', 'b') for c in chars):
                if len(chars) == 2:
                    cleaned = cleaned.replace(chars[0], 'X').replace(chars[1], 'Y')
                    cleaned = cleaned.replace('X', 'a').replace('Y', 'b')
                elif len(chars) == 1:
                    cleaned = cleaned.replace(chars[0], 'a')
                
            rev_dict = {v: k for k, v in self._bacon_dict.items()}
            out = ""
            for i in range(0, len(cleaned) - 4, 5):
                chunk = cleaned[i:i+5]
                out += rev_dict.get(chunk, "?")
            return self._create_result(True, output_text=out)
        else:
            out = ""
            for char in input_data.text.upper():
                if char in self._bacon_dict:
                    out += self._bacon_dict[char]
            return self._create_result(True, output_text=out)
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text:
            cleaned = re.sub(r'[^a-zA-Z]', '', input_data.text)
            if len(cleaned) >= 5 and len(set(cleaned.lower())) == 2:
                return 0.7, {"reason": "Consists of only two characters"}
        return 0.0, {}

class BeaufortDecoder(DecoderBase):
    name = "Beaufort Cipher"
    category = "classical"
    reversible = True
    input_types = ["text"]
    output_types = ["text"]
    description = "Decodes Beaufort cipher (requires key)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if not input_data.text: return self._create_result(False, errors=["Empty text"])
        key = context.get("key", "KEY").upper()
        key = re.sub(r'[^A-Z]', '', key)
        if not key: return self._create_result(False, errors=["Valid key required"])
        
        out = ""
        key_idx = 0
        for char in input_data.text.upper():
            if char.isalpha():
                # Beaufort: C = (K - P) mod 26 -> P = (K - C) mod 26
                k = ord(key[key_idx]) - 65
                c = ord(char) - 65
                p = (k - c) % 26
                out += chr(p + 65)
                key_idx = (key_idx + 1) % len(key)
            else:
                out += char
        return self._create_result(True, output_text=out)
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.0, {}
