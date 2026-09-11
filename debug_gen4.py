from app.services.candidate_generation import CandidateConfig, CandidateGenerator
from app.knowledge.registry import knowledge_registry

cfg = CandidateConfig(
    max_candidates=50000000,
    max_runtime_sec=60.0,
    enable_leetspeak=True,
    enable_mixed_case=True,
    enable_digit_suffix=True,
    enable_wrappers=True,
    max_combination_depth=3,
    suffixes=["2026"],
    wrappers=["TRON", "CTF"]
)

g = CandidateGenerator(cfg)
tron_words = knowledge_registry.get_tron_context_wordlist()

found_c1 = False
found_c2 = False
found_c3 = False
count = 0
for c in g.generate([], tron_words, []):
    count += 1
    if c.value == "TRON{Ne0n_C1rcu1t_D3f3nse_2026}":
        print(f"Found TRON{{Ne0n_C1rcu1t_D3f3nse_2026}} at count {count}!")
        found_c1 = True
    if c.value == "TRON{Cyb3r_D3f3ns3_2026}":
        print(f"Found TRON{{Cyb3r_D3f3ns3_2026}} at count {count}!")
        found_c2 = True
    if c.value == "CTF{N3tw0rk_F0r3ns1cs_2026}":
        print(f"Found CTF{{N3tw0rk_F0r3ns1cs_2026}} at count {count}!")
        found_c3 = True

if not (found_c1 and found_c2 and found_c3):
    print("Failed to find some generated candidates.")
