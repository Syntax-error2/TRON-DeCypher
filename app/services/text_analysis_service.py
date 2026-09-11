import math
import re
import string
from typing import Any


class TextAnalysisService:
    '''Reusable service for printability and text analysis.'''
    
    PRINTABLE = set(string.printable.encode('ascii'))
    
    # English letter frequencies
    ENGLISH_FREQ = {
        'A': 0.08167, 'B': 0.01492, 'C': 0.02782, 'D': 0.04253, 'E': 0.12702,
        'F': 0.02228, 'G': 0.02015, 'H': 0.06094, 'I': 0.06966, 'J': 0.00153,
        'K': 0.00772, 'L': 0.04025, 'M': 0.02406, 'N': 0.06749, 'O': 0.07507,
        'P': 0.01929, 'Q': 0.00095, 'R': 0.05987, 'S': 0.06327, 'T': 0.09056,
        'U': 0.02758, 'V': 0.00978, 'W': 0.02360, 'X': 0.00150, 'Y': 0.01974,
        'Z': 0.00074
    }

    COMMON_WORDS = {"THE", "BE", "TO", "OF", "AND", "A", "IN", "THAT", "HAVE", "I", "IT", "FOR", "NOT", "ON", "WITH", "HE", "AS", "YOU", "DO", "AT", "THIS"}
    COMMON_TRIGRAMS = {"THE", "AND", "THA", "ENT", "ING", "ION", "TIO", "FOR", "NDE", "HAS"}

    def analyze(self, data: bytes) -> dict[str, Any]:
        '''Analyze a byte sequence and return text heuristics.'''
        if not data:
            return {
                "printable_ratio": 0.0,
                "ascii_ratio": 0.0,
                "null_ratio": 0.0,
                "whitespace_ratio": 0.0,
                "is_valid_utf8": True,
                "is_probably_text": False
            }
            
        length = len(data)
        printable_count = 0
        ascii_count = 0
        null_count = 0
        ws_count = 0
        
        for byte in data:
            if byte in self.PRINTABLE:
                printable_count += 1
            if byte < 128:
                ascii_count += 1
            if byte == 0:
                null_count += 1
            if byte in b" \t\n\r":
                ws_count += 1
                
        is_valid_utf8 = True
        try:
            data.decode('utf-8')
        except UnicodeDecodeError:
            is_valid_utf8 = False
            
        printable_ratio = printable_count / length
        ascii_ratio = ascii_count / length
        null_ratio = null_count / length
        ws_ratio = ws_count / length
        
        is_probably_text = (printable_ratio > 0.9 or (is_valid_utf8 and ascii_ratio > 0.8)) and null_ratio < 0.05
        
        return {
            "printable_ratio": printable_ratio,
            "ascii_ratio": ascii_ratio,
            "null_ratio": null_ratio,
            "whitespace_ratio": ws_ratio,
            "is_valid_utf8": is_valid_utf8,
            "is_probably_text": is_probably_text
        }

    def score_english(self, text: str) -> float:
        '''Score a string for likelihood of being English text (0.0 to 1.0+).'''
        if not text:
            return 0.0
            
        upper_text = text.upper()
        letters = [c for c in upper_text if c.isalpha()]
        if not letters:
            return 0.0
            
        # Frequency score (Chi-squared or simple Bhattacharyya distance)
        counts = {chr(i): 0 for i in range(65, 91)}
        for c in letters:
            counts[c] += 1
            
        freq_score = 0.0
        for c, count in counts.items():
            obs = count / len(letters)
            exp = self.ENGLISH_FREQ.get(c, 0.0)
            freq_score += math.sqrt(obs * exp)
            
        # Word and Trigram score
        words = re.findall(r'\b[A-Z]+\b', upper_text)
        word_score = 0.0
        for w in words:
            if w in self.COMMON_WORDS:
                word_score += 0.05
                
        trigram_score = 0.0
        for i in range(len(upper_text) - 2):
            tri = upper_text[i:i+3]
            if tri in self.COMMON_TRIGRAMS:
                trigram_score += 0.02
                
        # Total score combining frequency overlap with structural cues
        return freq_score + word_score + trigram_score

text_analysis_service = TextAnalysisService()
