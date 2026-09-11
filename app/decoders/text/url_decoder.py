import time
import urllib.parse
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class UrlDecoder(DecoderBase):
    name = "url"
    version = "1.0.0"
    category = "Text"
    description = "Decodes URL percent-encoded strings."
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
            
        percent_count = text.count("%")
        if percent_count == 0:
            return 0.0, {}
            
        # Check if they are valid percent encodings (e.g. %20)
        valid_encodings = 0
        for i in range(len(text) - 2):
            if text[i] == "%" and text[i+1:i+3].isalnum(): # Rough check
                valid_encodings += 1
                    
        if valid_encodings == 0:
            return 0.0, {"reason": "no valid percent encodings found"}
            
        confidence = min(0.1 + (valid_encodings * 0.1), 0.9)
        return confidence, {"percent_count": percent_count, "reasons": [f"found {valid_encodings} percent encodings"]}

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        start_time = time.time()
        text = self._get_text(input_data)
        
        if not text:
            return self._create_result(False, errors=["Empty input"], start_time=start_time)
            
        try:
            decoded = urllib.parse.unquote(text)
            
            # If no change occurred, success but low confidence
            if decoded == text:
                return self._create_result(True, output_text=decoded, warnings=["No URL encoding found"], start_time=start_time)
                
            return self._create_result(
                success=True,
                output_text=decoded,
                start_time=start_time
            )
        except Exception as e:
            return self._create_result(False, errors=[str(e)], start_time=start_time)
