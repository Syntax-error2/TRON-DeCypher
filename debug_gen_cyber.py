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
cands = g.generate(master_words=[], context_words=["cyber", "defense"], category_words=[])

found = False
for c in cands:
    if c.value == "TRON{Cyb3r_D3f3ns3_2026}":
        found = True
        break
        
print("Found:", found)
