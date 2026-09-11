import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class XorDecoder(DecoderBase):
    name = "xor"
    version = "1.0.0"
    category = "Binary"
    description = "Single-byte and multi-byte XOR transformations."
    supported_input_types = ["bytes", "text"]
    
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
        # XOR is practically impossible to detect deterministically without a known plaintext or heuristic scoring
        # We return 0 confidence by default for detection
        return 0.0, {}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        data = self._get_bytes(input_data)
        
        if not data:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        key_param = context.get("key")
        if not key_param:
            return self._create_result(False, errors=["No XOR key provided"], start_time=start_time)
            
        # Parse key
        key_bytes = b""
        if isinstance(key_param, int):
            key_bytes = bytes([key_param % 256])
        elif isinstance(key_param, str):
            key_bytes = key_param.encode('utf-8')
        elif isinstance(key_param, bytes):
            key_bytes = key_param
            
        if not key_bytes:
            return self._create_result(False, errors=["Invalid XOR key"], start_time=start_time)
            
        key_len = len(key_bytes)
        
        try:
            # Perform XOR
            result_bytes = bytearray(len(data))
            for i, byte in enumerate(data):
                result_bytes[i] = byte ^ key_bytes[i % key_len]
                
            analysis = text_analysis_service.analyze(bytes(result_bytes))
            output_text = None
            if analysis["is_valid_utf8"] and analysis["printable_ratio"] > 0.5:
                output_text = result_bytes.decode('utf-8', errors='ignore')
                
            return self._create_result(
                success=True,
                output_text=output_text,
                output_data=bytes(result_bytes),
                metadata={"key_len": key_len, "analysis": analysis},
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
