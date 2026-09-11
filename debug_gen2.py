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
for c in g.generate(master_words=[], context_words=["neon", "circuit", "defense"], category_words=[]):
    if "Ne0n_C1rcu1t_D3f3nse" in c.value:
        print(c.value)
        found = True

if not found:
    print("Not found at all!")
