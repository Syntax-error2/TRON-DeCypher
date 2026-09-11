import re
from dataclasses import dataclass, field
from typing import Any

from app.decoders.core.models import DecoderInput
from app.decoders.core.registry import DecoderRegistry, decoder_registry
from app.services.hash_identification import hash_identification_service


@dataclass
class DetectionCandidate:
    decoder_name: str
    confidence: float
    is_hash: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

class DecoderDetectionService:
    def __init__(self, registry: DecoderRegistry | None = None):
        self.registry = registry or decoder_registry
        self.FLAG_PATTERN = re.compile(r'^(CTF|FLAG|TRON|HTB|THM)\{(.*?)\}$', re.IGNORECASE)

    def detect(self, input_data: DecoderInput, min_confidence: float = 0.0) -> list[DetectionCandidate]:
        candidates = []
        text = input_data.text.strip() if input_data.text else ""
        
        # Extract inner flag content for detection scoring
        m = self.FLAG_PATTERN.match(text)
        if m:
            text = m.group(2)
            input_data = DecoderInput(text=text, data=input_data.data, source_type=input_data.source_type, encoding=input_data.encoding)
        
        # 1. Hashes
        hash_cands = hash_identification_service.identify(text) if text else []
        has_strong_hash = False
        
        for hc in hash_cands:
            candidates.append(DetectionCandidate(
                decoder_name=hc.algorithm,
                confidence=hc.confidence,
                is_hash=True,
                metadata={'reasons': hc.reasons}
            ))
            if hc.confidence >= 0.90:
                has_strong_hash = True

        # 2. Encodings & Ciphers
        for decoder in self.registry.list_all():
            name = decoder.name
            if not getattr(decoder, 'reversible', True):
                continue
            
            try:
                result = decoder.detect(input_data)
                if isinstance(result, tuple):
                    conf, meta = result
                else:
                    conf = result
                    meta = {}
                
                # Suppress generic encodings if we have a strong hash candidate
                if has_strong_hash:
                    if name.lower() in ["hex", "base64", "base32", "url", "html"]:
                        # Cap confidence so they don't override the hash
                        conf = min(conf, 0.4)
                
                if conf > 0:
                    candidates.append(DetectionCandidate(
                        decoder_name=name,
                        confidence=conf,
                        is_hash=False,
                        metadata=meta
                    ))
            except Exception:
                continue

        candidates.sort(key=lambda x: x.confidence, reverse=True)
        return [c for c in candidates if c.confidence >= min_confidence]

decoder_detector = DecoderDetectionService()
