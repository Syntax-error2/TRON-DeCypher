with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('max_candidates=200_000,', 'max_candidates=200_000_000,')
content = content.replace('max_candidates=300_000,', 'max_candidates=200_000_000,')

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
