import base64
import re
import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class Base64Decoder(DecoderBase):
    name = "base64"
    version = "1.0.0"
    category = "Encoding"
    description = "Decodes Standard and URL-safe Base64."
    supported_input_types = ["text", "bytes"]
    
    B64_PATTERN = re.compile(b'^[A-Za-z0-9+/=]+$')
    URL_B64_PATTERN = re.compile(b'^[A-Za-z0-9\\-_=]+$')
    
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
        data = self._get_bytes(input_data)
        if not data:
            return 0.0, {}
            
        data = data.strip()
        length = len(data)
        if length == 0:
            return 0.0, {}
            
        reasons = []
        confidence = 0.0
        is_url_safe = False
        
        # Base64 characteristics
        if self.B64_PATTERN.match(data):
            reasons.append("matches standard base64 alphabet")
            confidence += 0.4
        elif self.URL_B64_PATTERN.match(data):
            reasons.append("matches URL-safe base64 alphabet")
            is_url_safe = True
            confidence += 0.4
        else:
            return 0.0, {"reason": "invalid characters for base64"}
            
        # Padding
        if length % 4 == 0:
            reasons.append("valid padding length (multiple of 4)")
            confidence += 0.2
        elif data.endswith(b"="):
            # Invalid length but has padding
            return 0.0, {"reason": "malformed padding"}
        else:
            reasons.append("unpadded but possible base64")
            confidence += 0.1
            
        # Attempt decode
        try:
            # Fix padding if missing
            pad_len = (4 - length % 4) % 4
            padded_data = data + (b"=" * pad_len)
            
            if is_url_safe:
                decoded = base64.urlsafe_b64decode(padded_data)
            else:
                decoded = base64.b64decode(padded_data)
                
            reasons.append("successful decode")
            confidence += 0.2
            
            # Analyze output
            analysis = text_analysis_service.analyze(decoded)
            if analysis["is_probably_text"]:
                reasons.append("decoded data is likely text")
                confidence += 0.15
            
        except Exception:
            return 0.0, {"reason": "decode failed"}
            
        # Cap confidence
        confidence = min(1.0, confidence)
        
        return confidence, {
            "reasons": reasons,
            "url_safe": is_url_safe,
            "decoded_size": len(decoded)
        }

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        data = self._get_bytes(input_data).strip()
        
        if not data:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        pad_len = (4 - len(data) % 4) % 4
        padded_data = data + (b"=" * pad_len)
        
        is_url_safe = context.get("url_safe", False)
        
        try:
            if is_url_safe or b"-" in data or b"_" in data:
                decoded = base64.urlsafe_b64decode(padded_data)
            else:
                decoded = base64.b64decode(padded_data)
                
            analysis = text_analysis_service.analyze(decoded)
            output_text = None
            if analysis["is_valid_utf8"] and analysis["printable_ratio"] > 0.5:
                output_text = decoded.decode('utf-8')
                
            return self._create_result(
                success=True,
                output_text=output_text,
                output_data=decoded,
                metadata={"url_safe": is_url_safe, "padded": pad_len > 0, "analysis": analysis},
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
