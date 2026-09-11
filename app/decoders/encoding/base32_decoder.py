import base64
import re
import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class Base32Decoder(DecoderBase):
    name = "base32"
    version = "1.0.0"
    category = "Encoding"
    description = "Decodes Base32."
    supported_input_types = ["text", "bytes"]
    
    B32_PATTERN = re.compile(b'^[A-Z2-7=]+$')
    
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, DecoderInput)
        
    def _get_bytes(self, input_data: DecoderInput) -> bytes:
        if input_data.data is not None:
            return input_data.data
        if input_data.text is not None:
            return input_data.text.encode(input_data.encoding, errors='ignore').upper()
        return b""

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        data = self._get_bytes(input_data).strip()
        if not data:
            return 0.0, {}
            
        reasons = []
        confidence = 0.0
        
        if self.B32_PATTERN.match(data):
            reasons.append("matches standard base32 alphabet")
            confidence += 0.4
        else:
            return 0.0, {"reason": "invalid characters for base32"}
            
        try:
            pad_len = (8 - len(data) % 8) % 8
            padded_data = data + (b"=" * pad_len)
            decoded = base64.b32decode(padded_data)
            
            reasons.append("successful decode")
            confidence += 0.2
            
            analysis = text_analysis_service.analyze(decoded)
            if analysis["is_probably_text"]:
                reasons.append("decoded data is likely text")
                confidence += 0.15
        except Exception:
            return 0.0, {"reason": "decode failed"}
            
        return min(1.0, confidence), {"reasons": reasons, "decoded_size": len(decoded)}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        data = self._get_bytes(input_data).strip()
        
        if not data:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        pad_len = (8 - len(data) % 8) % 8
        padded_data = data + (b"=" * pad_len)
        
        try:
            decoded = base64.b32decode(padded_data)
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
