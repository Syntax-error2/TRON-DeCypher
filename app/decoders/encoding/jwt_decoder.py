import json
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.web.analyzers.jwt_analyzer import jwt_analyzer


class JwtDecoder(DecoderBase):
    name = "JWT Decode"
    category = "encoding"
    reversible = False
    input_types = ["text"]
    output_types = ["text"]
    description = "Decodes a JSON Web Token (JWT) header and payload."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        if not input_data.text:
            return self._create_result(False, errors=["JWT requires text input"])
            
        token = input_data.text.strip()
        analysis = jwt_analyzer.analyze(token)
        if not analysis:
            return self._create_result(False, errors=["Invalid JWT format or unable to decode"])
            
        out = f"Header:\n{json.dumps(analysis.get('header', {}), indent=2)}\n\n"
        out += f"Payload:\n{json.dumps(analysis.get('payload', {}), indent=2)}"
        if "signature" in analysis:
            out += f"\n\nSignature:\n{analysis['signature']}"
            
        return self._create_result(True, output_text=out)
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.text:
            parts = input_data.text.strip().split(".")
            if len(parts) == 3 and parts[0].startswith("eyJ"):
                return 0.9, {"reason": "Standard JWT format (eyJ...)"}
        return 0.0, {}
