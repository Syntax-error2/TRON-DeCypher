from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult, HashResult
from app.services.hashing_service import hashing_service


class HashGenerator(DecoderBase):
    name = "Hash Generator"
    category = "hashing"
    reversible = False
    input_types = ["text", "bytes"]
    output_types = ["text"]
    description = "Generates a cryptographic hash or checksum."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        algo = context.get("algorithm", "md5").lower()
        if algo not in hashing_service.get_supported_algorithms():
            return self._create_result(False, errors=[f"Unsupported algorithm: {algo}"])
            
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        hashes = hashing_service.hash_bytes(data, [algo])
        if algo not in hashes:
            return self._create_result(False, errors=["Hashing failed"])
            
        digest = hashes[algo]
        
        hr = HashResult(
            algorithm=algo,
            digest=digest,
            input_type="bytes" if input_data.data else "text",
            input_size=len(data)
        )
        
        return self._create_result(True, output_text=digest, metadata={"hash_result": hr.model_dump()})
        
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        # Hash Generation is not auto-detected from plaintext, it's explicitly chosen
        return 0.0, {}
