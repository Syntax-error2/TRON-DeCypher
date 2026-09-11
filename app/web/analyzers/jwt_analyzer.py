import base64
import json
from typing import Any


class JWTAnalyzer:
    """Safely decodes and validates JWT structures without signature attacks."""
    
    def analyze(self, token: str) -> dict[str, Any] | None:
        parts = token.split(".")
        if len(parts) not in (2, 3):
            return None
            
        result = {}
        try:
            # Header
            header_padded = self._pad_base64(parts[0])
            result["header"] = json.loads(base64.urlsafe_b64decode(header_padded).decode('utf-8'))
            
            # Payload
            payload_padded = self._pad_base64(parts[1])
            result["payload"] = json.loads(base64.urlsafe_b64decode(payload_padded).decode('utf-8'))
            
            if len(parts) == 3:
                result["signature"] = parts[2]
                
            return result
        except Exception:
            return None
            
    def _pad_base64(self, b64_str: str) -> str:
        padding = 4 - (len(b64_str) % 4)
        if padding and padding < 4:
            return b64_str + ("=" * padding)
        return b64_str

jwt_analyzer = JWTAnalyzer()
