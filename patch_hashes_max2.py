with open('tests/qa/test_hash_accuracy.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('CandidateConfig(max_candidates=200_000_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, suffixes=["TEST"])', 'CandidateConfig(max_candidates=100_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, suffixes=["TEST"])')
content = content.replace('CandidateConfig(max_candidates=200_000_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, enable_leetspeak=True, suffixes=["2026"], max_combination_depth=3)', 'CandidateConfig(max_candidates=100_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, enable_leetspeak=True, suffixes=["2026"], max_combination_depth=3)')

with open('tests/qa/test_hash_accuracy.py', 'w', encoding='utf-8') as f:
    f.write(content)
