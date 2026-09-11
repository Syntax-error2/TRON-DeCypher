with open('tests/unit/test_symbol_decoder.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("# sorted_syms unused, we pass symbols directly to solve", "sorted_syms = direction_analyzer.sort_symbols(symbols, \"lr\")")

with open('tests/unit/test_symbol_decoder.py', 'w', encoding='utf-8') as f:
    f.write(content)
