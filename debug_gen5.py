import hashlib
from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig(
    enable_wrappers=True,
    enable_leetspeak=True,
    enable_digit_suffix=True,
    max_combination_depth=3,
    suffixes=["2026"]
)
g = CandidateGenerator(cfg)
cands = list(g.generate(master_words=[], context_words=["neon", "circuit", "defense"], category_words=[]))
found = False
for c in cands:
    if c.value == "TRON{Ne0n_C1rcu1t_D3f3nse_2026}":
        found = True
print("Found: ", found)
