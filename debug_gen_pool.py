from app.services.candidate_generation import CandidateConfig, CandidateGenerator
cfg = CandidateConfig(
    enable_wrappers=True,
    enable_leetspeak=True,
    enable_digit_suffix=True,
    max_combination_depth=2,
    suffixes=["2026"],
    wrappers=["TRON"]
)
g = CandidateGenerator(cfg)
context_words = ["neon", "circuit", "defense", "network", "forensics", "cyber", "stego"]
pool = []
for w in context_words[:10]:
    pool.append(w.capitalize())
    pool.append(w.lower())
    pool.extend(g.leet_mutations(w.capitalize()))
    pool.extend(g.leet_mutations(w.lower()))
    
pool = list(dict.fromkeys(pool))
print("Cyb3r" in pool)
print("D3f3ns3" in pool)
