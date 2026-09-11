from app.services.candidate_generation import (
    CandidateConfig,
    CandidateDeduplicator,
    CandidateGenerator,
)


def test_config():
    cfg = CandidateConfig()
    assert cfg.enable_leetspeak is True
    
def test_dedup():
    d = CandidateDeduplicator()
    assert d.is_new("hello") is True
    assert d.is_new("hello") is False

def test_case_mutations():
    cfg = CandidateConfig()
    g = CandidateGenerator(cfg)
    muts = g.case_mutations("Cyber")
    assert "cyber" in muts
    assert "CYBER" in muts
    
def test_leet_mutations():
    cfg = CandidateConfig(enable_mixed_case=False)
    g = CandidateGenerator(cfg)
    muts = g.leet_mutations("defense")
    assert "d3f3n53" in muts

def test_generate_priority():
    cfg = CandidateConfig(
        enable_wrappers=True,
        enable_leetspeak=True,
        enable_digit_suffix=True,
        max_combination_depth=1 # keep it simple for priority check
    )
    g = CandidateGenerator(cfg)
    cands = list(g.generate(master_words=["tron"], context_words=["cyber"], category_words=["stego"]))
    
    # 1. Exact base words (stego, cyber) -> Prio 100
    assert cands[0].value == "cyber"
    assert cands[0].priority == 100
    assert cands[1].value == "stego"
    assert cands[1].priority == 100
    
    # 2. Master word exact -> P100
    assert cands[2].value == "tron"
    assert cands[2].priority == 100
    
    # Check if CTK{cyber} is generated (priority 95)
    has_wrapper = any(c.value == "CTK{cyber}" for c in cands)
    assert has_wrapper
    
def test_required_md5_vector():
    # Target: 701c3d8c43ac57e2a1fd28a4936c02c7
    # Expected: CTK{Ne0n_C1rcu1t_D3f3nse_2026}
    cfg = CandidateConfig(
        enable_wrappers=True,
        enable_leetspeak=True,
        enable_digit_suffix=True,
        max_combination_depth=3,
        suffixes=["2026"]
    )
    g = CandidateGenerator(cfg)
    # Give it the base words
    # Neon Circuit Defense -> Ne0n_C1rcu1t_D3f3nse_2026 -> CTK{}
    cands = g.generate(master_words=[], context_words=["neon", "circuit", "defense"], category_words=[])
    
    found = False
    for c in cands:
        if c.value == "CTK{Ne0n_C1rcu1t_D3f3nse_2026}":
            found = True
            break
            
    assert found
