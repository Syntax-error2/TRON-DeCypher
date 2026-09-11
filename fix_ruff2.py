with open('tests/unit/test_symbol_decoder.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines):
    if 'def test_output_type_safety(tmp_path) -> None:' in line or 'def test_output_type_safety(tmp_path):' in line:
        start_idx = i
        for j in range(start_idx, len(lines)):
            if 'sorted_syms = direction_analyzer.sort_symbols(symbols, "lr")' in lines[j]:
                lines[j] = lines[j].replace('sorted_syms = direction_analyzer.sort_symbols(symbols, "lr")', '# removed unused sorted_syms')
                break
        break

with open('tests/unit/test_symbol_decoder.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
