import re
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class DecimalAsciiDecoder(DecoderBase):
    name = "Decimal ASCII"
    category = "numeric"
    reversible = True
    input_types = ["text"]
    output_types = ["bytes"]
    description = "Decodes decimal ASCII (e.g. 72 101 108 108 111)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if not input_data.text: return self._create_result(False, errors=["Empty input"])
        mode = context.get("mode", "decode")
        try:
            if mode == "decode":
                nums = re.findall(r'\d+', input_data.text)
                out = bytes(int(n) for n in nums if 0 <= int(n) <= 255)
                return self._create_result(True, output_data=out, output_text=out.decode('utf-8', errors='ignore'))
            else:
                data = input_data.text.encode('utf-8')
                out_txt = " ".join(str(b) for b in data)
                return self._create_result(True, output_text=out_txt)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text and re.match(r'^(\d{1,3}\s+)+\d{1,3}$', input_data.text.strip()):
            nums = [int(x) for x in input_data.text.strip().split()]
            if all(0 <= n <= 255 for n in nums):
                return 0.7, {"reason": "Looks like decimal ASCII"}
        return 0.0, {}

class OctalAsciiDecoder(DecoderBase):
    name = "Octal ASCII"
    category = "numeric"
    reversible = True
    input_types = ["text"]
    output_types = ["bytes"]
    description = "Decodes octal ASCII (e.g. 110 145 154 154 157)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if not input_data.text: return self._create_result(False, errors=["Empty input"])
        mode = context.get("mode", "decode")
        try:
            if mode == "decode":
                nums = re.findall(r'[0-7]+', input_data.text)
                out = bytes(int(n, 8) for n in nums if 0 <= int(n, 8) <= 255)
                return self._create_result(True, output_data=out, output_text=out.decode('utf-8', errors='ignore'))
            else:
                data = input_data.text.encode('utf-8')
                out_txt = " ".join(oct(b)[2:] for b in data)
                return self._create_result(True, output_text=out_txt)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text and re.match(r'^([0-7]{1,3}\s+)+[0-7]{1,3}$', input_data.text.strip()):
            return 0.6, {"reason": "Looks like octal ASCII"}
        return 0.0, {}

class BitwiseNotDecoder(DecoderBase):
    name = "Bitwise NOT"
    category = "binary"
    reversible = True
    input_types = ["bytes", "text"]
    output_types = ["bytes"]
    description = "Flips all bits in the input."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        out = bytes(~b & 0xFF for b in data)
        return self._create_result(True, output_data=out)
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.0, {}

class ByteSwapDecoder(DecoderBase):
    name = "Byte Swap"
    category = "binary"
    reversible = True
    input_types = ["bytes", "text"]
    output_types = ["bytes"]
    description = "Swaps adjacent bytes (16-bit word swap)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        out = bytearray(data)
        for i in range(0, len(out) - 1, 2):
            out[i], out[i+1] = out[i+1], out[i]
        return self._create_result(True, output_data=bytes(out))
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.0, {}
