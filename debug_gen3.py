from app.services.candidate_generation import CandidateConfig, CandidateGenerator
from app.knowledge.registry import knowledge_registry

cfg = CandidateConfig(
    max_candidates=500000,
    max_runtime_sec=10.0,
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

found = False
for c in g.generate([], tron_words, []):
    if "Ne0n_C1rcu1t_D3f3nse" in c.value:
        print(c.value)
        found = True

if not found:
    print("Still not found!")
