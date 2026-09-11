import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the forced_words hack
patch = '''
    def generate(self, master_words: list[str], context_words: list[str], category_words: list[str]) -> Iterator[Candidate]:
        all_base = list(dict.fromkeys(category_words + context_words + master_words))
'''
content = re.sub(r'    def generate\(self, master_words: list\[str\], context_words: list\[str\], category_words: list\[str\]\) -> Iterator\[Candidate\]:\n(?:.*\n){1,5}?        all_base = list\(dict\.fromkeys\(category_words \+ context_words \+ master_words\)\)', patch.strip('\n'), content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
