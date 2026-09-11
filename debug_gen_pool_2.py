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
cands = g.generate(master_words=[], context_words=["neon", "circuit", "defense", "network", "forensics", "cyber", "stego"], category_words=[])

found_depth2 = False
found_depth2_suffix = False
for c in cands:
    if c.value == "Cyb3r_D3f3ns3":
        found_depth2 = True
    if c.value == "Cyb3r_D3f3ns3_2026":
        found_depth2_suffix = True
        
print("Depth 2:", found_depth2)
print("Depth 2 Suffix:", found_depth2_suffix)
