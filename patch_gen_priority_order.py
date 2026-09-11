import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('all_base = list(dict.fromkeys(category_words + context_words + master_words))', 'all_base = list(dict.fromkeys(context_words + category_words + master_words))')
content = content.replace('high_priority_base = list(dict.fromkeys(category_words + context_words))', 'high_priority_base = list(dict.fromkeys(context_words + category_words))')

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
