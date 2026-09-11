import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
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
'''
content = re.sub(r'    def _yield_wrapped\(self, c_val: str, prio: int, source: str, mut: str\) -> Iterator\[Candidate\]:\n(?:.*\n){1,6}?                    yield Candidate\(cw, prio - 5, source, f"\{mut\} \+ Wrapper"\)', patch.strip('\n'), content)

# Now replace _yield_wrapped calls in Depth 2 and 3 to have dedup=False
content = content.replace('_yield_wrapped(c, 55, "Combo", "Depth 2")', '_yield_wrapped(c, 55, "Combo", "Depth 2", dedup=False)')
content = content.replace('_yield_wrapped(cs, 54, "Combo", "Depth 2 + Suffix")', '_yield_wrapped(cs, 54, "Combo", "Depth 2 + Suffix", dedup=False)')
content = content.replace('_yield_wrapped(c, 50, "Combo", "Depth 3")', '_yield_wrapped(c, 50, "Combo", "Depth 3", dedup=False)')
content = content.replace('_yield_wrapped(cs, 45, "Combo", "Depth 3 + Suffix")', '_yield_wrapped(cs, 45, "Combo", "Depth 3 + Suffix", dedup=False)')

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
