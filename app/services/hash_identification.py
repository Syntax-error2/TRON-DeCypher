from app.crypto.hashes.hash_identifier import hash_identifier
from app.decoders.core.models import HashCandidate


class HashIdentificationService:
    def identify(self, text: str) -> list[HashCandidate]:
        results = hash_identifier.identify(text)
        return [
            HashCandidate(
                algorithm=r.algorithm,
                confidence=r.confidence,
                length_match=True,
                charset_match=True,
                prefix_match=r.is_structured,
                reasons=r.reasons
            )
            for r in results
        ]

hash_identification_service = HashIdentificationService()
