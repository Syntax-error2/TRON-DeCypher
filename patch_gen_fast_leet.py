import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
    def leet_mutations(self, word: str) -> list[str]:
        if not self.config.enable_leetspeak:
            return []
            
        replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'A': '4', 'E': '3', 'I': '1', 'O': '0', 'S': '5', 'T': '7'}
        
        muts = []
        
        # 1. Full replace
        res1 = ""
        for c in word:
            res1 += replacements.get(c, c)
        muts.append(res1)
        
        # 2. Vowels only
        vowel_replacements = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 'A': '4', 'E': '3', 'I': '1', 'O': '0'}
        res2 = ""
        for c in word:
            res2 += vowel_replacements.get(c, c)
        muts.append(res2)
        
        # 3. Vowels only, but skip the last character if it's 'e' or 's'
        # This handles words like "Defense" -> "D3f3nse" which is common in CTFs
        res3 = ""
        for i, c in enumerate(word):
            if i == len(word) - 1 and c.lower() in ('e', 's', 't'):
                res3 += c
            else:
                res3 += vowel_replacements.get(c, c)
        muts.append(res3)
        
        final_muts = []
        for m in list(dict.fromkeys(muts)):
            final_muts.append(m)
            if self.config.enable_mixed_case:
                final_muts.append(m.capitalize())
                final_muts.append(m.upper())
                
        return list(dict.fromkeys(final_muts))
'''
content = re.sub(r'    def leet_mutations\(self, word: str\) -> list\[str\]:\n(?:.*\n){1,30}?        return list\(dict\.fromkeys\(final_muts\)\)', patch.strip('\n'), content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
