import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the function index and replace it manually to be safe.
start_idx = content.find('def generate(self, master_words: list[str]')
end_idx = content.find('all_base = list(dict.fromkeys(category_words', start_idx)

new_func = '''def generate(self, master_words: list[str], context_words: list[str], category_words: list[str]) -> Iterator[Candidate]:
        '''

content = content[:start_idx] + new_func + content[end_idx:]

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
