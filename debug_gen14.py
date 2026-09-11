from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig(
    enable_wrappers=True,
    enable_leetspeak=True,
    enable_digit_suffix=True,
    max_combination_depth=3,
    suffixes=["2026"]
)
g = CandidateGenerator(cfg)
found = False
count = 0
for c in g.generate(master_words=[], context_words=["neon", "circuit", "defense"], category_words=[]):
    count += 1
    if c.value == "TRON{Ne0n_C1rcu1t_D3f3nse_2026}":
        print(f"FOUND at {count}!")
        found = True
        break
        
print("Count:", count)
print("Found:", found)
