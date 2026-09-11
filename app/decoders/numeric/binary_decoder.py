import re
import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class BinaryAsciiDecoder(DecoderBase):
    name = "binary"
    version = "1.0.0"
    category = "Numeric"
    description = "Decodes ASCII Binary strings (e.g. 01001000)."
    supported_input_types = ["text", "bytes"]
    
    BIN_CLEAN = re.compile(b'[^01]')
    
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
            
        zeros = data.count(b"0")
        ones = data.count(b"1")
        spaces = data.count(b" ")
        
        total_valid = zeros + ones + spaces
        
        if total_valid < len(data) * 0.9: # Allow a few other chars just in case, but usually strict
            return 0.0, {"reason": "contains many non-binary characters"}
            
        cleaned = self.BIN_CLEAN.sub(b'', data)
        if len(cleaned) % 8 != 0:
            return 0.0, {"reason": "length is not a multiple of 8"}
            
        confidence = 0.6
        if spaces > 0:
            confidence += 0.2
            
        return confidence, {"reasons": ["looks like binary text"]}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        data = self._get_bytes(input_data).strip()
        
        if not data:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        cleaned = self.BIN_CLEAN.sub(b'', data)
        if len(cleaned) % 8 != 0:
            return self._create_result(False, errors=["Binary string length is not a multiple of 8"], start_time=start_time)
            
        try:
            # Parse binary string
            b_str = cleaned.decode('ascii')
            decoded = bytearray(int(b_str[i:i+8], 2) for i in range(0, len(b_str), 8))
            
            analysis = text_analysis_service.analyze(bytes(decoded))
            
            output_text = None
            if analysis["is_valid_utf8"] and analysis["printable_ratio"] > 0.5:
                output_text = decoded.decode('utf-8')
                
            return self._create_result(
                success=True,
                output_text=output_text,
                output_data=bytes(decoded),
                metadata={"analysis": analysis},
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
