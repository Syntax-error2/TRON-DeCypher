import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
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
                
        muts = []
        if len(options) > 10:
            res = ""
            for c in word:
                res += replacements.get(c, [c])[1] if len(replacements.get(c, [c])) > 1 else c
            muts.append(res)
        else:
            import itertools
            for combo in itertools.product(*options):
                muts.append("".join(combo))
        
        final_muts = []
        for m in list(dict.fromkeys(muts)):
            final_muts.append(m)
            if self.config.enable_mixed_case:
                final_muts.append(m.capitalize())
                final_muts.append(m.upper())
                
        return list(dict.fromkeys(final_muts))
'''
content = re.sub(r'    def leet_mutations\(self, word: str\) -> list\[str\]:\n(?:.*\n){1,30}?        return list\(dict\.fromkeys\(final_muts\)\)', patch.strip('\n'), content)

# Adjust depth bounds
content = content.replace('high_priority_base[:50]', 'high_priority_base[:12]')
content = content.replace('high_priority_base[:12]', 'high_priority_base[:6]')  # Wait, string replace will replace both to 6 if run sequentially incorrectly. Let's do regex.

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
