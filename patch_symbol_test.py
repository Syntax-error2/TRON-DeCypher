with open('tests/unit/test_symbol_decoder.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("CTF{A}", "CTK{A}")
content = content.replace("CTF{HASH_RECOVERY_TEST}", "CTK{HASH_RECOVERY_TEST}")

with open('tests/unit/test_symbol_decoder.py', 'w', encoding='utf-8') as f:
    f.write(content)
