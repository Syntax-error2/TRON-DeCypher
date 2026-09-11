import codecs
import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class UnicodeEscapeDecoder(DecoderBase):
    name = "unicode_escape"
    version = "1.0.0"
    category = "Text"
    description = "Decodes Unicode escapes (e.g. \\u0048)."
    supported_input_types = ["text", "bytes"]
    
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, DecoderInput)
        
    def _get_text(self, input_data: DecoderInput) -> str:
        if input_data.text is not None:
            return input_data.text
        if input_data.data is not None:
            return input_data.data.decode(input_data.encoding, errors='ignore')
        return ""

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = self._get_text(input_data)
        if not text:
            return 0.0, {}
            
        count = text.count("\\u")
        if count == 0:
            count = text.count("\\U")
            
        if count == 0:
            return 0.0, {}
            
        confidence = min(0.2 + (count * 0.1), 0.9)
        return confidence, {"reasons": [f"found {count} unicode escape sequences"]}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        text = self._get_text(input_data)
        
        if not text:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        try:
            # Codecs unicode_escape decodes \uXXXX to characters
            decoded = codecs.decode(text, 'unicode_escape')
            if decoded == text:
                return self._create_result(True, output_text=decoded, warnings=["No unicode escapes found"], start_time=start_time)
                
            return self._create_result(
                success=True,
                output_text=decoded,
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
