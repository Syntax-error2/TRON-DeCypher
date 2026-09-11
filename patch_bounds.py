import re
with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix bounds properly
content = re.sub(r'for w in high_priority_base\[:\d+\]:\s+# P55', r'for w in high_priority_base[:12]:', content)
content = re.sub(r'for w in high_priority_base\[:\d+\]: \s+# P50', r'for w in high_priority_base[:6]:', content)

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
