import itertools
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class CandidateConfig:
    max_candidates: int = 5_000_000
    max_runtime_sec: float = 60.0
    enable_leetspeak: bool = True
    enable_mixed_case: bool = True
    enable_digit_suffix: bool = True
    enable_wrappers: bool = True
    max_combination_depth: int = 3
    separators: list[str] = field(default_factory=lambda: ["_", "-", ".", "@"])
    suffixes: list[str] = field(default_factory=lambda: ["2024", "2025", "2026", "1337", "0", "1", "123", "404"])
    wrappers: list[str] = field(default_factory=lambda: ["CTK", "FLAG", "TRON"])

@dataclass
class Candidate:
    value: str
    priority: int
    source: str
    mutation: str
    depth: int = 1

class CandidateDeduplicator:
    def __init__(self) -> None:
        self.seen = set()
        
    def is_new(self, candidate: str) -> bool:
        h = hash(candidate)
        if h in self.seen:
            return False
        self.seen.add(h)
        return True

class CandidateGenerator:
    def __init__(self, config: CandidateConfig) -> None:
        self.config = config
        self.dedup = CandidateDeduplicator()
        
    def simple_leet(self, word: str) -> str:
        # Standard CTF vowel replacements to hit combinations without combinatorial explosion
        replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 'A': '4', 'E': '3', 'I': '1', 'O': '0'}
        res = ""
        for c in word:
            res += replacements.get(c, c)
        return res
        
    def leet_mutations(self, word: str) -> list[str]:
        if not self.config.enable_leetspeak:
            return []
            
        replacements = {'a': ['a', '4'], 'e': ['e', '3'], 'i': ['i', '1'], 'o': ['o', '0'], 's': ['s', '5'], 't': ['t', '7'], 'A': ['A', '4'], 'E': ['E', '3'], 'I': ['I', '1'], 'O': ['O', '0'], 'S': ['S', '5'], 'T': ['T', '7']}
        options = []
        for c in word:
            if c in replacements:
                options.append(replacements[c])
            else:
                options.append([c])
                
        import itertools
        muts = []
        for combo in itertools.product(*options):
            muts.append("".join(combo))
        
        final_muts = []
        for m in list(dict.fromkeys(muts)):
            final_muts.append(m)
            if self.config.enable_mixed_case:
                final_muts.append(m.capitalize())
                final_muts.append(m.upper())
                
        return list(dict.fromkeys(final_muts))

    def case_mutations(self, word: str) -> list[str]:
        if not self.config.enable_mixed_case:
            return [word]
        return list(dict.fromkeys([word, word.lower(), word.capitalize(), word.upper()]))

    def _yield_wrapped(self, c_val: str, prio: int, source: str, mut: str, dedup: bool = True) -> Iterator[Candidate]:
        if dedup:
            if not self.dedup.is_new(c_val):
                return
                
        yield Candidate(c_val, prio, source, mut)
        if self.config.enable_wrappers:
            for wr in self.config.wrappers:
                cw = f"{wr}{{{c_val}}}"
                if not dedup or self.dedup.is_new(cw):
                    yield Candidate(cw, prio - 5, source, f"{mut} + Wrapper")
        
    def generate(self, master_words: list[str], context_words: list[str], category_words: list[str]) -> Iterator[Candidate]:
        all_base = list(dict.fromkeys(context_words + category_words + master_words))
        high_priority_base = list(dict.fromkeys(context_words + category_words))
        
        # P100: Exact Base Words
        for w in all_base:
            if self.dedup.is_new(w):
                yield Candidate(w, 100, "Base", "Exact")
                
        # P95: Wrappers on base words
        if self.config.enable_wrappers:
            for w in all_base:
                for wr in self.config.wrappers:
                    cw = f"{wr}{{{w}}}"
                    if self.dedup.is_new(cw):
                        yield Candidate(cw, 95, "Base", "Wrapper")
                        
        # P90: Simple Case Mutations on High Priority
        for w in high_priority_base:
            for m in self.case_mutations(w):
                yield from self._yield_wrapped(m, 90, "Context/Category", "Case")
                    
        # P80: Base Word + Suffix
        if self.config.enable_digit_suffix:
            for w in high_priority_base:
                for c_mut in self.case_mutations(w):
                    for suf in self.config.suffixes:
                        yield from self._yield_wrapped(f"{c_mut}{suf}", 80, "Base", "Suffix")
                            
        # P75: Base Word + Separator + Suffix
        if self.config.enable_digit_suffix:
            for w in high_priority_base:
                for c_mut in self.case_mutations(w):
                    for sep in self.config.separators:
                        for suf in self.config.suffixes:
                            yield from self._yield_wrapped(f"{c_mut}{sep}{suf}", 75, "Base", "Sep+Suffix")

        # P65: Leetspeak
        if self.config.enable_leetspeak:
            for w in high_priority_base:
                words_to_leet = [w, w.capitalize()]
                for lw in words_to_leet:
                    for m in self.leet_mutations(lw):
                        yield from self._yield_wrapped(m, 65, "Base", "Leetspeak")
                        if self.config.enable_digit_suffix:
                            for sep in self.config.separators + [""]:
                                for suf in self.config.suffixes:
                                    yield from self._yield_wrapped(f"{m}{sep}{suf}", 63, "Base", "Leetspeak+Suffix")
                        
        # P55: Word Combinations (Depth 2)
        if self.config.max_combination_depth >= 2:
            pool = []
            for w in high_priority_base[:10]:
                pool.append(w.capitalize())
                pool.append(w.lower())
                if self.config.enable_leetspeak:
                    pool.extend(self.leet_mutations(w.capitalize()))
                    pool.extend(self.leet_mutations(w.lower()))
            pool = list(dict.fromkeys(pool))
            
            for combo in itertools.product(pool, repeat=2):
                for sep in self.config.separators + [""]:
                    c = sep.join(combo)
                    yield from self._yield_wrapped(c, 55, "Combo", "Depth 2", dedup=False)
                    if self.config.enable_digit_suffix:
                        for suf in self.config.suffixes:
                            cs = f"{c}{sep}{suf}" if sep else f"{c}_{suf}"
                            yield from self._yield_wrapped(cs, 54, "Combo", "Depth 2 + Suffix", dedup=False)
                                            
        # P50: Word Combinations (Depth 3)
        if self.config.max_combination_depth >= 3:
            small_pool = []
            for w in high_priority_base[:4]: 
                small_pool.append(w.capitalize())
                small_pool.append(w.lower())
                if self.config.enable_leetspeak:
                    small_pool.extend(self.leet_mutations(w.capitalize()))
            small_pool = list(dict.fromkeys(small_pool))
            
            for combo in itertools.product(small_pool, repeat=3):
                for sep in self.config.separators:
                    c = sep.join(combo)
                    yield from self._yield_wrapped(c, 50, "Combo", "Depth 3", dedup=False)
                    if self.config.enable_digit_suffix:
                        for suf in self.config.suffixes:
                            cs = f"{c}{sep}{suf}"
                            yield from self._yield_wrapped(cs, 45, "Combo", "Depth 3 + Suffix", dedup=False)

        # Finally, stream master words
        for w in master_words:
            for m in self.case_mutations(w):
                yield from self._yield_wrapped(m, 20, "Master", "Case")

