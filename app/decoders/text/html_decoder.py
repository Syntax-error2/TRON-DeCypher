import html
import time
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class HtmlDecoder(DecoderBase):
    name = "html"
    version = "1.0.0"
    category = "Text"
    description = "Decodes HTML entities."
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
            
        entities = text.count("&")
        if entities == 0:
            return 0.0, {}
            
        if ";" not in text:
            return 0.0, {}
            
        decoded = html.unescape(text)
        if decoded != text:
            return 0.8, {"reasons": ["contains valid HTML entities"]}
            
        return 0.0, {}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        text = self._get_text(input_data)
        
        if not text:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        try:
            decoded = html.unescape(text)
            if decoded == text:
                return self._create_result(True, output_text=decoded, warnings=["No HTML entities found"], start_time=start_time)
                
            return self._create_result(
                success=True,
                output_text=decoded,
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
