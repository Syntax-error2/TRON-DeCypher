from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult
from app.services.text_analysis_service import text_analysis_service


class RailFenceDecoder(DecoderBase):
    name = "Rail Fence Cipher"
    category = "classical_ciphers"
    description = "Transposition cipher reading zig-zag across rails."
    expected_params = {
        "rails": {"type": "int", "default": 3, "description": "Number of rails (2-20)"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"},
        "auto_crack": {"type": "bool", "default": False, "description": "Try all rails"}
    }
    
    def _transform(self, text: str, rails: int, decrypt: bool) -> str:
        text = "".join(text.split()) # Rail fence typically ignores spaces, but we can preserve if needed. 
        # Actually standard rail fence applies to the whole string including spaces.
        if rails <= 1:
            return text
            
        if not decrypt:
            fence = [[] for _ in range(rails)]
            rail = 0
            direction = 1
            for char in text:
                fence[rail].append(char)
                rail += direction
                if rail == rails - 1 or rail == 0:
                    direction *= -1
            return "".join("".join(rail) for rail in fence)
        else:
            fence = [["\n"] * len(text) for _ in range(rails)]
            rail = 0
            direction = 1
            for i in range(len(text)):
                fence[rail][i] = "*"
                rail += direction
                if rail == rails - 1 or rail == 0:
                    direction *= -1
                    
            idx = 0
            for r in range(rails):
                for c in range(len(text)):
                    if fence[r][c] == "*" and idx < len(text):
                        fence[r][c] = text[idx]
                        idx += 1
                        
            result = []
            rail = 0
            direction = 1
            for i in range(len(text)):
                result.append(fence[rail][i])
                rail += direction
                if rail == rails - 1 or rail == 0:
                    direction *= -1
            return "".join(result)

    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        auto_crack = context.get("auto_crack", False)
        
        if auto_crack and decrypt:
            best_score = -1.0
            best_text = ""
            best_rails = 2
            
            candidates = []
            max_rails = min(20, len(text))
            for r in range(2, max_rails):
                cand = self._transform(text, r, True)
                score = text_analysis_service.score_english(cand)
                candidates.append((score, r, cand))
                if score > best_score:
                    best_score = score
                    best_text = cand
                    best_rails = r
                    
            candidates.sort(reverse=True, key=lambda x: x[0])
            top_cands = [{"score": c[0], "parameters": f"Rails: {c[1]}", "candidate": c[2]} for c in candidates[:5]]
            
            return self._create_result(
                True, 
                output_text=best_text, 
                metadata={"best_rails": best_rails, "candidates": top_cands, "auto_crack": True}
            )
        else:
            try:
                rails = int(context.get("rails", 3))
            except ValueError:
                return self._create_result(False, errors=["Rails must be an integer"])
                
            dec = self._transform(text, rails, decrypt)
            return self._create_result(True, output_text=dec)

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {"reason": "Possible Rail Fence"}

class ScytaleDecoder(DecoderBase):
    name = "Scytale"
    category = "classical_ciphers"
    description = "Transposition cipher using a cylinder (diameter = columns)."
    expected_params = {
        "columns": {"type": "int", "default": 4, "description": "Number of columns (diameter)"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"}
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        
        try:
            cols = int(context.get("columns", 4))
        except ValueError:
            return self._create_result(False, errors=["Columns must be an integer"])
            
        if cols <= 1:
            return self._create_result(True, output_text=text)
            
        import math
        rows = math.ceil(len(text) / cols)
        
        # Pad text
        padded_text = text + " " * (rows * cols - len(text))
        
        if decrypt:
            # When decrypting, we read down the columns.
            # Which is essentially encoding with 'rows' as columns.
            result = []
            for r in range(cols):
                for c in range(rows):
                    result.append(padded_text[c * cols + r])
            return self._create_result(True, output_text="".join(result).strip())
        else:
            result = []
            for r in range(rows):
                for c in range(cols):
                    result.append(padded_text[c * rows + r])
            return self._create_result(True, output_text="".join(result).strip())

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {}

class ColumnarTranspositionDecoder(DecoderBase):
    name = "Columnar Transposition"
    category = "classical_ciphers"
    description = "Transposition cipher using a keyword."
    expected_params = {
        "key": {"type": "str", "default": "KEY", "description": "Keyword"},
        "mode": {"type": "str", "default": "decrypt", "description": "encrypt or decrypt"}
    }
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        text = input_data.text
        if not text:
            return self._create_result(False, errors=["Empty input"])
            
        key = context.get("key", "KEY")
        mode = context.get("mode", "decrypt")
        decrypt = mode.lower() != "encrypt"
        
        # Determine column order from key (handles repeated chars by appearing left-to-right)
        key_order = []
        for i, char in enumerate(key):
            key_order.append((char, i))
        key_order.sort()
        
        cols = len(key)
        import math
        rows = math.ceil(len(text) / cols)
        
        if decrypt:
            # Figure out lengths of each column
            col_lengths = [rows] * cols
            short_cols = (rows * cols) - len(text)
            for i in range(cols - 1, cols - 1 - short_cols, -1):
                col_lengths[i] -= 1
                
            # Read columns based on key_order
            grid = [["" for _ in range(cols)] for _ in range(rows)]
            idx = 0
            for char, orig_col in key_order:
                col_len = col_lengths[orig_col]
                for r in range(col_len):
                    if idx < len(text):
                        grid[r][orig_col] = text[idx]
                        idx += 1
                        
            result = []
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c]:
                        result.append(grid[r][c])
            return self._create_result(True, output_text="".join(result))
        else:
            grid = [["" for _ in range(cols)] for _ in range(rows)]
            idx = 0
            for r in range(rows):
                for c in range(cols):
                    if idx < len(text):
                        grid[r][c] = text[idx]
                        idx += 1
                        
            result = []
            for char, orig_col in key_order:
                for r in range(rows):
                    if grid[r][orig_col]:
                        result.append(grid[r][orig_col])
            return self._create_result(True, output_text="".join(result))

    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.05, {}
