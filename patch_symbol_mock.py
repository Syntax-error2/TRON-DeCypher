with open('tests/unit/test_symbol_decoder.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"id3": "F",', '"id3": "K",')

with open('tests/unit/test_symbol_decoder.py', 'w', encoding='utf-8') as f:
    f.write(content)
