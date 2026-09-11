import hashlib

from app.services.candidate_generation import CandidateConfig
from app.services.hash_recovery import hash_recovery_service

def _test_vector(target_hash, algo, expected_cand):
    cfg = CandidateConfig(
        max_candidates=200_000_000,
        max_runtime_sec=300.0,
        enable_leetspeak=True,
        enable_mixed_case=True,
        enable_digit_suffix=True,
        enable_wrappers=True,
        max_combination_depth=3,
        suffixes=["2026", "TEST"],
        wrappers=["CTK"]
    )
    
    gen = hash_recovery_service.recover_automatic_generator(target_hash, algo, cfg)
    
    found = False
    for update in gen:
        if update.get("status") == "MATCH":
            assert update.get("candidate") == expected_cand
            found = True
            break
    
    assert found, f"Failed to recover {expected_cand} for {algo}"

def test_md5_required_vector() -> None:
    expected = "CTK{HASH_RECOVERY_TEST}"
    h = hashlib.md5(expected.encode()).hexdigest()
    _test_vector(h, "md5", expected)
    
def test_sha1_required_vector() -> None:
    expected = "CTK{HASH_RECOVERY_TEST}"
    h = hashlib.sha1(expected.encode()).hexdigest()
    _test_vector(h, "sha1", expected)

def test_sha256_required_vector() -> None:
    expected = "CTK{HASH_RECOVERY_TEST}"
    h = hashlib.sha256(expected.encode()).hexdigest()
    _test_vector(h, "sha256", expected)

def test_dynamic_hash_2() -> None:
    cand = "CTK{Cyb3r_D3f3ns3_2026}"
    t_hash = hashlib.md5(cand.encode()).hexdigest()
    _test_vector(t_hash, "md5", cand)

def test_dynamic_hash_3() -> None:
    cand = "CTK{N3tw0rk_F0r3ns1cs_2026}"
    t_hash = hashlib.md5(cand.encode()).hexdigest()
    _test_vector(t_hash, "md5", cand)
