with open('tests/unit/test_symbol_decoder.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("id_a = [k for k, v in id_freq.items() if v == 3][0]", "id_a = next(k for k, v in id_freq.items() if v == 3)")
content = content.replace("sorted_syms = direction_analyzer.sort_symbols(symbols, \"lr\")", "# sorted_syms unused, we pass symbols directly to solve")

with open('tests/unit/test_symbol_decoder.py', 'w', encoding='utf-8') as f:
    f.write(content)
