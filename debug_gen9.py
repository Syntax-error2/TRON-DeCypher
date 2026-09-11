from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig(
    enable_wrappers=True,
    enable_leetspeak=True,
    enable_digit_suffix=True,
    max_combination_depth=3,
    suffixes=["2026"],
    wrappers=["TRON", "CTF"]
)
g = CandidateGenerator(cfg)

found_1 = False
count = 0
for c in g.generate(master_words=[], context_words=["neon", "circuit", "defense"], category_words=[]):
    count += 1
    if c.value == "TRON{Ne0n_C1rcu1t_D3f3nse_2026}":
        found_1 = True
        break
        
print("Count: ", count)
print("Found 1: ", found_1)
