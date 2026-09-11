import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
    def simple_leet(self, word: str) -> str:
        replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7'}
        res = ""
        for c in word:
            res += replacements.get(c, c)
        return res
'''
# inject simple_leet
if "def simple_leet(" not in content:
    content = content.replace('    def case_mutations(self, word: str) -> list[str]:', patch.strip() + '\n\n    def case_mutations(self, word: str) -> list[str]:')

# Fix P55
patch_p55 = '''
        # P55: Word Combinations (Depth 2)
        if self.config.max_combination_depth >= 2:
            pool = []
            for w in high_priority_base[:50]:
                pool.append(w.capitalize())
                pool.append(w.lower())
                if self.config.enable_leetspeak:
                    pool.append(self.simple_leet(w.capitalize()))
                    pool.append(self.simple_leet(w.lower()))
            pool = list(dict.fromkeys(pool))
'''
content = re.sub(r'        # P55: Word Combinations \(Depth 2\)\n(?:.*\n){2,10}?            pool = list\(dict\.fromkeys\(pool\)\)', patch_p55.strip('\n'), content)

# Fix P50
patch_p50 = '''
        # P50: Word Combinations (Depth 3)
        if self.config.max_combination_depth >= 3:
            small_pool = []
            for w in high_priority_base[:15]: 
                small_pool.append(w.capitalize())
                small_pool.append(w.lower())
                if self.config.enable_leetspeak:
                    small_pool.append(self.simple_leet(w.capitalize()))
            small_pool = list(dict.fromkeys(small_pool))
'''
content = re.sub(r'        # P50: Word Combinations \(Depth 3\)\n(?:.*\n){2,10}?            small_pool = list\(dict\.fromkeys\(small_pool\)\)', patch_p50.strip('\n'), content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
