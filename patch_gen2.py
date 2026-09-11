import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
    def simple_leet(self, word: str) -> str:
        # Standard CTF vowel replacements to hit combinations without combinatorial explosion
        replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 'A': '4', 'E': '3', 'I': '1', 'O': '0'}
        res = ""
        for c in word:
            res += replacements.get(c, c)
        return res
'''
content = re.sub(r'    def simple_leet\(self, word: str\) -> str:\n(?:.*\n){1,6}?        return res', patch.strip('\n'), content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
