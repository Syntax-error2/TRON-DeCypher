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

count = 0
found = False
for c in g.generate(master_words=[], context_words=["neon", "circuit", "defense"], category_words=[]):
    count += 1
    if c.value == "TRON{Ne0n_C1rcu1t_D3f3nse_2026}":
        print("Found at count:", count)
        found = True
        break
        
print("Count:", count)
print("Found:", found)
