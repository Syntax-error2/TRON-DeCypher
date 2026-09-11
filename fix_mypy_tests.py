import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    # basic def test_xyz() -> None:
    content = re.sub(r'def (test_[a-zA-Z0-9_]+)\(\):', r'def \1() -> None:', content)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_file('tests/unit/test_knowledge.py')
fix_file('tests/unit/test_classical_decoders.py')
fix_file('tests/unit/test_symbol_decoder.py')
fix_file('tests/unit/test_ui_decoder_link.py')
