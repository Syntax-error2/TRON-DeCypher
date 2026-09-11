from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig(
    enable_wrappers=True,
    enable_leetspeak=True,
    enable_digit_suffix=True,
    max_combination_depth=3,
    suffixes=["2026"],
    wrappers=["TRON"]
)
g = CandidateGenerator(cfg)
context_words = ["neon", "circuit", "defense", "network", "forensics", "cyber", "stego"]
cands = g.generate(master_words=[], context_words=context_words, category_words=[])

found = False
count = 0
for c in cands:
    count += 1
    if c.value == "TRON{Ne0n_C1rcu1t_D3f3nse_2026}":
        found = True
        break
        
print("Found:", found, "at count:", count)
