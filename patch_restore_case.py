import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''    def case_mutations(self, word: str) -> list[str]:
        if not self.config.enable_mixed_case:
            return [word]
        return list(dict.fromkeys([word, word.lower(), word.capitalize(), word.upper()]))

    def _yield_wrapped'''
    
content = content.replace('    def _yield_wrapped', patch)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
