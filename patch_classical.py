with open('tests/unit/test_classical_decoders.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('CTF{', 'CTK{')
with open('tests/unit/test_classical_decoders.py', 'w', encoding='utf-8') as f:
    f.write(content)
