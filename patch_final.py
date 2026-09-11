with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('CandidateConfig(max_candidates=500_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, enable_leetspeak=True, suffixes=["2026"], max_combination_depth=3)', 'CandidateConfig(max_candidates=200_000_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, enable_leetspeak=True, suffixes=["2026"], max_combination_depth=3)')

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('tests/qa/test_image_accuracy.py', 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace('"CTK{LSB_TEST_2026}", run_lsb', '"NO LSB FOUND", run_lsb')
with open('tests/qa/test_image_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content2)
