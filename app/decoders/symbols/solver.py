from app.decoders.symbols.direction import direction_analyzer
from app.decoders.symbols.models import SymbolItem, SymbolResult
from app.services.text_analysis_service import text_analysis_service


class SymbolSolver:
    def solve(self, symbols: list[SymbolItem], custom_mapping: dict[str, str], profile_mapping: dict[str, str] = None) -> SymbolResult:
        result = SymbolResult(detected_symbols=symbols)
        result.unique_symbols = len(set(s.symbol_id for s in symbols))
        
        profile_mapping = profile_mapping or {}
        
        # Test directions
        directions = ["lr", "rl", "tb", "bt"]
        candidates = []
        
        # Determine actual mapping to use (custom overrides profile)
        active_mapping = profile_mapping.copy()
        for k, v in custom_mapping.items():
            if v: # don't overwrite with empty
                active_mapping[k] = v
                
        result.mapping_used = active_mapping
        
        # 1. Evaluate Direct Mapped Strings
        for d in directions:
            sorted_syms = direction_analyzer.sort_symbols(symbols, d)
            text_chars = []
            for s in sorted_syms:
                char = active_mapping.get(s.symbol_id, "?")
                text_chars.append(char)
            text = "".join(text_chars)
            
            # Score
            score = text_analysis_service.score_english(text)
            
            # CTF flag boost
            if "CTK{" in text or "FLAG{" in text or "TRON{" in text or "CTF{" in text:
                score += 5.0
                
            candidates.append({"text": text, "direction": d, "score": score, "type": "mapped"})
            
        # 2. Evaluate Frequency Substitution if unmapped/partial
        unmapped_ids = set(s.symbol_id for s in symbols if s.symbol_id not in active_mapping)
        if unmapped_ids and len(symbols) >= 10:
            # simple freq substitution attempt
            for d in directions:
                sorted_syms = direction_analyzer.sort_symbols(symbols, d)
                freqs: dict[str, int] = {}
                for s in sorted_syms:
                    freqs[s.symbol_id] = freqs.get(s.symbol_id, 0) + 1
                    
                sorted_ids = sorted(freqs.keys(), key=lambda k: freqs[k], reverse=True)
                eng_freq = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
                
                sub_map = active_mapping.copy()
                eng_idx = 0
                for sid in sorted_ids:
                    if sid not in sub_map and eng_idx < len(eng_freq):
                        sub_map[sid] = eng_freq[eng_idx]
                        eng_idx += 1
                        
                text_chars = []
                for s in sorted_syms:
                    text_chars.append(sub_map.get(s.symbol_id, "?"))
                text = "".join(text_chars)
                
                score = text_analysis_service.score_english(text)
                if "CTK{" in text or "CTF{" in text: score += 5.0
                candidates.append({"text": text, "direction": d, "score": score, "type": "substitution"})
                
        # Sort candidates
        candidates.sort(key=lambda x: float(str(x["score"])), reverse=True)
        result.candidates = candidates
        
        if candidates:
            result.best_candidate = candidates[0]["text"]
            result.confidence = min(1.0, candidates[0]["score"] / 2.0) # naive normalization
            
        return result

solver = SymbolSolver()
