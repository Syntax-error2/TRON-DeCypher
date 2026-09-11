from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig(
    enable_wrappers=True,
    enable_leetspeak=True,
    enable_digit_suffix=True,
    max_combination_depth=3,
    suffixes=["2026"]
)
g = CandidateGenerator(cfg)
pool = []
for w in ["neon", "circuit", "defense"]:
    pool.append(w.capitalize())
    pool.append(w.lower())
    pool.extend(g.leet_mutations(w.capitalize()))
pool = list(dict.fromkeys(pool))
print(pool)
