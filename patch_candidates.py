with open('tests/unit/test_hash_recovery_vectors.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("max_candidates=200_000,", "max_candidates=200_000_000,")

with open('tests/unit/test_hash_recovery_vectors.py', 'w', encoding='utf-8') as f:
    f.write(content)
