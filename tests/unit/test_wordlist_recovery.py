from app.knowledge.flag_detection import flag_detection_service
from app.knowledge.registry import knowledge_registry
from app.services.hash_recovery import hash_recovery_service


def test_wordlist_size():
    master = knowledge_registry.get_master_wordlist()
    assert len(master) >= 5000, f"Expected 5000+ words, got {len(master)}"
    
def test_flag_detection():
    flags = flag_detection_service.detect("Here is the flag CTF{HASH_RECOVERY_TEST} end", "Test")
    assert len(flags) == 1
    assert flags[0].value == "CTF{HASH_RECOVERY_TEST}"

def run_recovery(target, algo):
    gen = hash_recovery_service.recover_automatic_generator(target, algo)
    last_res = None
    for res in gen:
        last_res = res
        if res.get('status') == 'MATCH':
            break
    return last_res

def test_md5_recovery():
    res = run_recovery("5d41402abc4b2a76b9719d911017c592", "md5")
    assert res is not None
    assert res['status'] == 'MATCH'
    assert res['candidate'] == 'hello'

def test_sha1_recovery():
    res = run_recovery("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d", "sha1")
    assert res is not None
    assert res['status'] == 'MATCH'
    assert res['candidate'] == 'hello'

def test_sha256_recovery():
    res = run_recovery("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824", "sha256")
    assert res is not None
    assert res['status'] == 'MATCH'
    assert res['candidate'] == 'hello'

def test_not_in_wordlist():
    import hashlib
    # a completely random string not in wordlist
    target = "SuperUnlikelyRandomString9999XYZ"
    h = hashlib.md5(target.encode()).hexdigest()
    res = run_recovery(h, "md5")
    assert res is not None
    assert res['status'] in ['NO_MATCH', 'LIMIT_REACHED']
