from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class MorseDecoder(DecoderBase):
    name = "Morse Code"
    category = "classical_ciphers"
    description = "Decodes Morse code strings (dots/dashes) into text, or encodes text."
    expected_params = {
        "mode": {"type": "str", "default": "decode", "description": "encode or decode"}
    }
    
    MORSE_MAP = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z', '.----': '1', '..---': '2', '...--': '3',
        '....-': '4', '.....': '5', '-....': '6', '--...': '7',
        '---..': '8', '----.': '9', '-----': '0', '--..--': ',',
        '.-.-.-': '.', '..--..': '?', '-..-.': '/', '-....-': '-',
        '-.--.': '(', '-.--.-': ')'
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decode")
        decrypt = mode.lower() != "encode"
        
        if decrypt:
            words = text.split("   ") # 3 spaces for word boundary commonly
            if not words or len(words) == 1:
                # sometimes just 1 space is used
                if " / " in text:
                    words = text.split(" / ")
                elif "  " in text:
                    words = text.split("  ")
                else:
                    words = [text]
                    
            decoded = []
            for w in words:
                chars = w.split()
                w_str = "".join([self.MORSE_MAP.get(c, "?") for c in chars])
                decoded.append(w_str)
                
            return self._create_result(True, output_text=" ".join(decoded).strip())
        else:
            rev_map = {v: k for k, v in self.MORSE_MAP.items()}
            result = []
            for word in text.upper().split():
                m_word = " ".join([rev_map.get(c, "") for c in word if c in rev_map])
                result.append(m_word)
            return self._create_result(True, output_text="   ".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        text = input_data.text
        if not text:
            return 0.0, {}
        text_clean = text.replace(" ", "").replace("/", "")
        if len(text_clean) > 0 and all(c in ".-" for c in text_clean):
            return 0.8, {"reason": "Consists entirely of dots, dashes, spaces, and slashes."}
        return 0.0, {}
