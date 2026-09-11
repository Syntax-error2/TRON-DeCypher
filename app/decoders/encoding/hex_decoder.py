import binascii
import re
import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class HexDecoder(DecoderBase):
    name = "hex"
    version = "1.0.0"
    category = "Encoding"
    description = "Decodes Hexadecimal (Base16) strings."
    supported_input_types = ["text", "bytes"]
    
    HEX_CLEAN = re.compile(b'[^0-9a-fA-F]')
    
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, DecoderInput)
        
    def _get_bytes(self, input_data: DecoderInput) -> bytes:
        if input_data.data is not None:
            return input_data.data
        if input_data.text is not None:
            return input_data.text.encode(input_data.encoding, errors='ignore')
        return b""

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        data = self._get_bytes(input_data).strip()
        if not data:
            return 0.0, {}
            
        # Quick check for 0x prefix and strip
        if data.startswith((b"0x", b"0X")):
            data = data[2:]
            
        # Count hex vs non-hex
        hex_chars = 0
        non_hex_chars = 0
        spaces = 0
        
        for b in data:
            if (b >= 48 and b <= 57) or (b >= 65 and b <= 70) or (b >= 97 and b <= 102): # 0-9 A-F a-f
                hex_chars += 1
            elif b in (32, 9, 10, 13, 44, 45, 58): # space, tab, nl, cr, comma, dash, colon
                spaces += 1
            else:
                non_hex_chars += 1
                
        if non_hex_chars > 0:
            return 0.0, {"reason": "contains invalid non-hex characters"}
            
        if hex_chars == 0 or hex_chars % 2 != 0:
            return 0.0, {"reason": "odd number of hex characters"}
            
        reasons = []
        confidence = 0.5
        
        if spaces > 0:
            reasons.append(f"found {spaces} separators")
            confidence += 0.1
            
        cleaned = self.HEX_CLEAN.sub(b'', data)
        try:
            decoded = binascii.unhexlify(cleaned)
            reasons.append("successful hex decode")
            confidence += 0.2
            
            analysis = text_analysis_service.analyze(decoded)
            if analysis["is_probably_text"]:
                reasons.append("decoded data is likely text")
                confidence += 0.15
        except Exception:
            return 0.0, {"reason": "unhexlify failed"}
            
        return min(1.0, confidence), {"reasons": reasons, "decoded_size": len(decoded)}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        data = self._get_bytes(input_data).strip()
        
        if not data:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        if data.startswith((b"0x", b"0X")):
            data = data[2:]
            
        cleaned = self.HEX_CLEAN.sub(b'', data)
        
        try:
            decoded = binascii.unhexlify(cleaned)
            analysis = text_analysis_service.analyze(decoded)
            
            output_text = None
            if analysis["is_valid_utf8"] and analysis["printable_ratio"] > 0.5:
                output_text = decoded.decode('utf-8')
                
            return self._create_result(
                success=True,
                output_text=output_text,
                output_data=decoded,
                metadata={"analysis": analysis},
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
