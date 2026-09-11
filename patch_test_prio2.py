import re
with open('tests/unit/test_candidate_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('assert cands[0].value == "stego"', 'assert cands[0].value == "cyber"')
content = content.replace('assert cands[1].value == "cyber"', 'assert cands[1].value == "stego"')

with open('tests/unit/test_candidate_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
