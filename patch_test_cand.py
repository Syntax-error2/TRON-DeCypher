with open('tests/unit/test_candidate_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("CTF{", "CTK{")
content = content.replace("TRON{", "CTK{")
content = content.replace("FLAG{", "CTK{")
content = content.replace("CTF}", "CTK}")

with open('tests/unit/test_candidate_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
