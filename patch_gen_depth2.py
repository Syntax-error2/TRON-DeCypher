import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the FIRST occurrence of [:4] with [:10]
content = content.replace('high_priority_base[:4]', 'high_priority_base[:10]', 1)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
