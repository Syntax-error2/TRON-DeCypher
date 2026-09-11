import time

from app.crypto.models import CryptoInput, CryptoResult
from app.services.text_analysis_service import text_analysis_service


class XorAnalyzer:
    """Single-byte and repeating-key XOR analytical engine."""
    
    def analyze_single_byte(self, crypto_input: CryptoInput) -> CryptoResult:
        start_time = time.time()
        
        data = crypto_input.get_bytes()
        if not data:
            return CryptoResult("XOR Single-Byte", "crack", False, execution_time=time.time()-start_time)
            
        candidates = []
        
        for key in range(256):
            decoded = bytes([b ^ key for b in data])
            # Use the existing Phase 2 text analyzer to score
            analysis = text_analysis_service.analyze(decoded)
            
            printable_ratio = analysis.get("printable_ratio", 0.0)
            
            if printable_ratio > 0.6:  # Threshold to avoid keeping total garbage
                decoded_str = decoded.decode('ascii', errors='replace')
                
                # Bonus for whitespace which is common in english text
                space_count = decoded_str.count(' ')
                space_ratio = space_count / len(decoded) if len(decoded) > 0 else 0
                
                score = (printable_ratio * 100) + (space_ratio * 100)
                
                candidates.append({
                    "key": hex(key),
                    "key_int": key,
                    "score": score,
                    "printable_ratio": printable_ratio,
                    "preview": decoded_str[:100] + ("..." if len(decoded_str) > 100 else "")
                })
                
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        confidence = 0.0
        if candidates and candidates[0]["printable_ratio"] > 0.9:
            confidence = 0.9
            
        observations = []
        if candidates:
            observations.append(f"Top candidate key: {candidates[0]['key']} with printable ratio {candidates[0]['printable_ratio']:.2f}")
            
        return CryptoResult(
            algorithm="XOR Single-Byte",
            operation="crack",
            success=True,
            confidence=confidence,
            candidates=candidates,
            observations=observations,
            execution_time=time.time()-start_time
        )
        
    def analyze_repeating_key(self, crypto_input: CryptoInput, max_key_len: int = 40) -> CryptoResult:
        """Estimates repeating key XOR lengths using normalized Hamming distance."""
        start_time = time.time()
        data = crypto_input.get_bytes()
        
        if len(data) < 10:
            return CryptoResult("XOR Repeating-Key", "analyze", False, execution_time=time.time()-start_time)
            
        max_len = min(max_key_len, len(data) // 2)
        
        distances = []
        for keysize in range(2, max_len + 1):
            if len(data) >= keysize * 4:
                # Take 4 blocks to average
                blocks = [data[i*keysize : (i+1)*keysize] for i in range(4)]
                dist1 = self._hamming_distance(blocks[0], blocks[1])
                dist2 = self._hamming_distance(blocks[2], blocks[3])
                dist3 = self._hamming_distance(blocks[0], blocks[2])
                dist4 = self._hamming_distance(blocks[1], blocks[3])
                avg_dist = (dist1 + dist2 + dist3 + dist4) / 4.0
                norm_dist = avg_dist / keysize
                distances.append({"key_length": keysize, "normalized_distance": norm_dist})
                
        distances.sort(key=lambda x: x["normalized_distance"])
        
        # Take top 3 likely key lengths
        top_lengths = distances[:3]
        
        return CryptoResult(
            algorithm="XOR Repeating-Key",
            operation="analyze",
            success=True,
            confidence=0.8 if top_lengths else 0.0,
            candidates=top_lengths,
            observations=[f"Likely key lengths: {[x['key_length'] for x in top_lengths]}"],
            execution_time=time.time()-start_time
        )
        
    def _hamming_distance(self, b1: bytes, b2: bytes) -> int:
        return sum((x ^ y).bit_count() for x, y in zip(b1, b2))

xor_analyzer = XorAnalyzer()
