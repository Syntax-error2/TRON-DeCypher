import base64
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class Base85Decoder(DecoderBase):
    name = "Base85 / ASCII85"
    category = "encoding"
    reversible = True
    input_types = ["text", "bytes"]
    output_types = ["bytes"]
    description = "Decodes Base85 (b85) or ASCII85 (a85)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decode")
        variant = context.get("variant", "b85") # 'b85' or 'a85'
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        
        try:
            if mode == "decode":
                if variant == "b85":
                    out = base64.b85decode(data)
                else:
                    out = base64.a85decode(data)
            else:
                if variant == "b85":
                    out = base64.b85encode(data)
                else:
                    out = base64.a85encode(data)
            return self._create_result(True, output_data=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        # Hard to detect generically without false positives
        return 0.0, {}

ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

class Base58Decoder(DecoderBase):
    name = "Base58"
    category = "encoding"
    reversible = True
    input_types = ["text", "bytes"]
    output_types = ["bytes"]
    description = "Decodes Base58 (Bitcoin alphabet)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decode")
        data = input_data.data if input_data.data else (input_data.text.encode('ascii', errors='ignore') if input_data.text else b"")
        try:
            if mode == "decode":
                out = self._decode_b58(data)
            else:
                out = self._encode_b58(data)
            return self._create_result(True, output_data=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def _decode_b58(self, data: bytes) -> bytes:
        pad = 0
        for b in data:
            if b == ALPHABET[0]:
                pad += 1
            else:
                break
        n = 0
        for b in data:
            idx = ALPHABET.index(b)
            n = n * 58 + idx
        res: list[int] = []
        while n > 0:
            n, r = divmod(n, 256)
            res.insert(0, r)
        return bytes([0]*pad + res)
        
    def _encode_b58(self, data: bytes) -> bytes:
        pad = 0
        for b in data:
            if b == 0:
                pad += 1
            else:
                break
        n = int.from_bytes(data, 'big')
        res: list[int] = []
        while n > 0:
            n, r = divmod(n, 58)
            res.insert(0, ALPHABET[r])
        return bytes([ALPHABET[0]]*pad + res)
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text and input_data.text.startswith("1") and len(input_data.text) > 25:
            # Bitcoin addresses start with 1
            return 0.6, {"reason": "Looks like Base58 Bitcoin address"}
        return 0.0, {}

