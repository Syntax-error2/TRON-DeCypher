import json
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class PunycodeDecoder(DecoderBase):
    name = "Punycode"
    category = "text"
    reversible = True
    input_types = ["text"]
    output_types = ["text"]
    description = "Decodes internationalized domain names (Punycode)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decode")
        if not input_data.text:
            return self._create_result(False, errors=["Text input required"])
            
        try:
            if mode == "decode":
                out = input_data.text.encode('ascii').decode('idna')
            else:
                out = input_data.text.encode('idna').decode('ascii')
            return self._create_result(True, output_text=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text and "xn--" in input_data.text:
            return 0.8, {"reason": "Contains 'xn--' prefix"}
        return 0.0, {}

class JsonEscapeDecoder(DecoderBase):
    name = "JSON Escapes"
    category = "text"
    reversible = True
    input_types = ["text"]
    output_types = ["text"]
    description = "Unescapes JSON strings (e.g., \\n, \\u0041)."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decode")
        if not input_data.text:
            return self._create_result(False, errors=["Text input required"])
            
        try:
            if mode == "decode":
                out = json.loads(f'"{input_data.text}"')
            else:
                out = json.dumps(input_data.text)[1:-1]
            return self._create_result(True, output_text=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text and "\\u" in input_data.text:
            return 0.5, {"reason": "Contains unicode escapes"}
        return 0.0, {}
