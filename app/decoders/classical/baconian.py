from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class BaconianDecoder(DecoderBase):
    name = "Baconian Cipher"
    category = "classical_ciphers"
    description = "Substitution cipher replacing each letter with 5 A/B characters."
    expected_params = {
        "mode": {"type": "str", "default": "decode", "description": "encode or decode"},
        "alphabet": {"type": "str", "default": "standard", "description": "standard (26) or classic (24)"}
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decode")
        decrypt = mode.lower() != "encode"
        alphabet_type = context.get("alphabet", "standard")
        
        # Standard A-Z (26 letters)
        std_dict = {chr(i + ord('A')): format(i, '05b').replace('0', 'A').replace('1', 'B') for i in range(26)}
        
        # Classic (24 letters, I=J, U=V)
        classic_dict = {}
        idx = 0
        for char in "ABCDEFGHIKLMNOPQRSTUWXYZ":
            classic_dict[char] = format(idx, '05b').replace('0', 'A').replace('1', 'B')
            idx += 1
        classic_dict['J'] = classic_dict['I']
        classic_dict['V'] = classic_dict['U']
        
        mapping = std_dict if alphabet_type == "standard" else classic_dict
        rev_mapping = {v: k for k, v in mapping.items()}
        
        if decrypt:
            clean_text = "".join([c.upper() for c in text if c.upper() in ['A', 'B']])
            if len(clean_text) % 5 != 0:
                return self._create_result(False, errors=["Ciphertext length must be a multiple of 5 A/B characters."])
                
            result = []
            for i in range(0, len(clean_text), 5):
                chunk = clean_text[i:i+5]
                result.append(rev_mapping.get(chunk, "?"))
            return self._create_result(True, output_text="".join(result))
        else:
            result = []
            for char in text.upper():
                if char.isalpha() and char in mapping:
                    result.append(mapping[char])
            return self._create_result(True, output_text=" ".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text:
            return 0.0, {}
        clean_text = "".join([c.upper() for c in text if c.isalpha()])
        if len(clean_text) > 0 and len(clean_text) % 5 == 0:
            if all(c in ['A', 'B'] for c in clean_text):
                return 0.8, {"reason": "Consists entirely of A and B in multiples of 5"}
        return 0.0, {}
