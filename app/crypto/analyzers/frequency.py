import string
import time
from collections import Counter

from app.crypto.models import CryptoInput, CryptoResult


class FrequencyAnalysisService:
    """Calculates single character frequencies, N-grams, and Index of Coincidence."""
    
    # Standard English character frequencies (approximate percentages)
    ENGLISH_FREQ = {
        'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 13.0, 'F': 2.2,
        'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.77, 'L': 4.0,
        'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.09, 'R': 6.0,
        'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 0.98, 'W': 2.4, 'X': 0.15,
        'Y': 2.0, 'Z': 0.07
    }
    
    def analyze(self, crypto_input: CryptoInput) -> CryptoResult:
        start_time = time.time()
        
        if isinstance(crypto_input.value, bytes):
            text = crypto_input.value.decode('utf-8', errors='ignore')
        else:
            text = crypto_input.value
            
        # Clean text for classical analysis (uppercase, letters only)
        letters_only = ''.join([c.upper() for c in text if c.upper() in string.ascii_uppercase])
        
        if not letters_only:
            return CryptoResult(
                algorithm="Frequency", operation="analyze", success=False,
                errors=["No alphabetic characters found."], execution_time=time.time()-start_time
            )
            
        N = len(letters_only)
        counts = Counter(letters_only)
        
        # Calculate frequencies
        frequencies = {char: (count / N) * 100 for char, count in counts.items()}
        
        # Calculate Index of Coincidence
        ioc = 0.0
        if N > 1:
            ioc_sum = sum(count * (count - 1) for count in counts.values())
            # Normalize IOC to the English standard (where ~1.73 is English, 1.0 is random)
            # Standard formula: sum(f*(f-1)) / (N*(N-1))
            # English IoC is ~0.0667, Random is ~0.0385 (for 26 letters)
            # We scale it: (ioc_sum / (N*(N-1))) * 26
            raw_ioc = ioc_sum / (N * (N - 1))
            ioc = raw_ioc * 26.0
            
        observations = []
        if 1.6 <= ioc <= 1.85:
            observations.append(f"IoC is {ioc:.2f} (English-like). Likely monoalphabetic substitution or transposition.")
        elif ioc < 1.4:
            observations.append(f"IoC is {ioc:.2f} (Random-like). Likely polyalphabetic (e.g. Vigenere) or modern encryption.")
            
        return CryptoResult(
            algorithm="Frequency",
            operation="analyze",
            success=True,
            confidence=1.0,
            parameters={
                "counts": dict(counts),
                "frequencies": frequencies,
                "ioc": ioc,
                "length": N
            },
            observations=observations,
            execution_time=time.time()-start_time
        )
        
frequency_analysis_service = FrequencyAnalysisService()
