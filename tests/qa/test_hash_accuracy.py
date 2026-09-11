import hashlib
import time
import tests.qa.qa_framework as qa
from app.services.hash_identification import hash_identification_service
from app.services.hash_recovery import hash_recovery_service, CandidateConfig



from app.knowledge.challenge_context import context_manager

def setup_context():
    context_manager.current_context.custom_dictionary = ["hash_recovery_test", "neon", "circuit", "defense"]
    # Mock the master wordlist so it's super fast
    from app.knowledge.registry import knowledge_registry
    

setup_context()

def run_hash_generator(target, algo, cfg):
    for step in hash_recovery_service.recover_automatic_generator(target, algo, cfg):
        if step.get('status') == 'MATCH':
            return step.get('candidate')
    return None

def get_hash(algo: str, plaintext: str) -> str:
    if algo == 'md5': return hashlib.md5(plaintext.encode()).hexdigest()
    if algo == 'sha1': return hashlib.sha1(plaintext.encode()).hexdigest()
    if algo == 'sha256': return hashlib.sha256(plaintext.encode()).hexdigest()
    if algo == 'sha512': return hashlib.sha512(plaintext.encode()).hexdigest()
    if algo == 'md4':
        try:
            return hashlib.new('md4', plaintext.encode()).hexdigest()
        except: return ""
    return ""

def identify_top_hash(target: str) -> str:
    cands = hash_identification_service.identify(target)
    if not cands: return "UNKNOWN"
    return cands[0].algorithm.lower()

def run_tests():
    # 8. Hash Identification QA
    test_hello = "hello"
    
    for algo in ["md4", "md5", "sha1", "sha256", "sha512"]:
        h = get_hash(algo, test_hello)
        if not h: continue
        # Identify should rank the correct hash at top
        qa.run_qa_test(f"HASH-ID-{algo.upper()}", "Hash Identification", algo.upper(), h, algo.lower(), identify_top_hash)

    # 10. Hash Recovery Accuracy
    cfg = CandidateConfig(max_candidates=100_000, enable_mixed_case=False)
    for algo in ["md5", "sha1", "sha256"]:
        h = get_hash(algo, test_hello)
        qa.run_qa_test(f"HASH-REC-01-{algo.upper()}", "Hash Recovery", algo.upper(), h, test_hello, 
            lambda x, a=algo: run_hash_generator(x, a, cfg))
            
    # 11. CTF Hash Test
    ctf_target = "CTK{HASH_RECOVERY_TEST}"
    cfg_ctf = CandidateConfig(max_candidates=100_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, suffixes=["TEST"])
    for algo in ["md5", "sha1", "sha256"]:
        h = get_hash(algo, ctf_target)
        qa.run_qa_test(f"HASH-REC-02-{algo.upper()}", "Hash Recovery", f"CTF {algo.upper()}", h, ctf_target, 
            lambda x, a=algo: run_hash_generator(x, a, cfg_ctf))
            
    # 12. Harder Candidate Test
    hard_target = "CTK{Ne0n_C1rcu1t_D3f3nse_2026}"
    h_hard = get_hash("md5", hard_target)
    cfg_hard = CandidateConfig(max_candidates=200_000_000, enable_wrappers=True, wrappers=["CTK"], enable_mixed_case=True, enable_leetspeak=True, suffixes=["2026"], max_combination_depth=3)
    qa.run_qa_test("HASH-REC-03", "Hash Recovery", "Hard CTF", h_hard, hard_target, 
        lambda x: run_hash_generator(x, "md5", cfg_hard))

    # 13. No-Match Test
    h_rand = get_hash("md5", "ThisIsARandomStringThatWillNotBeFoundInAnyWordlist")
    qa.run_qa_test("HASH-REC-04", "Hash Recovery", "No Match", h_rand, None, 
        lambda x: run_hash_generator(x, "md5", cfg))

