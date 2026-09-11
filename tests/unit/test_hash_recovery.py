from pathlib import Path

from app.services.hash_identification import hash_identification_service
from app.services.hash_recovery import hash_recovery_service


def test_hash_identification_md5() -> None:
    res = hash_identification_service.identify("5d41402abc4b2a76b9719d911017c592")
    assert any(c.algorithm == "md5" for c in res)
    assert res[0].algorithm == "md5"

def test_hash_identification_sha1() -> None:
    res = hash_identification_service.identify("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")
    assert res[0].algorithm == "sha1"

def test_hash_identification_sha256() -> None:
    res = hash_identification_service.identify("2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
    assert res[0].algorithm == "sha256"
    
def test_hash_identification_sha512() -> None:
    h = "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043"
    res = hash_identification_service.identify(h)
    assert res[0].algorithm == "sha512"

def test_verify_candidate_match() -> None:
    # hello -> MD5
    res = hash_recovery_service.verify_candidate("5d41402abc4b2a76b9719d911017c592", "md5", "hello")
    assert res.status == "MATCH"
    assert res.candidate == "hello"
    
    # admin -> MD5
    res = hash_recovery_service.verify_candidate("21232f297a57a5a743894a0e4a801fc3", "md5", "admin")
    assert res.status == "MATCH"

def test_verify_candidate_nomatch() -> None:
    res = hash_recovery_service.verify_candidate("5d41402abc4b2a76b9719d911017c592", "md5", "wrong")
    assert res.status == "NO_MATCH"
    assert res.candidate is None
    
def test_wordlist_recovery(tmp_path: Path) -> None:
    wl = tmp_path / "wordlist.txt"
    wl.write_text("wrong\nadmin\npassword\nhello\nsecret")
    
    gen = hash_recovery_service.recover_wordlist_generator("5d41402abc4b2a76b9719d911017c592", "md5", wl)
    res = list(gen)
    
    assert len(res) == 1
    assert res[-1]["status"] == "MATCH"
    assert res[-1]["candidate"] == "hello"

def test_wordlist_recovery_no_match(tmp_path: Path) -> None:
    wl = tmp_path / "wordlist.txt"
    wl.write_text("wrong\nadmin\npassword\nsecret")
    
    gen = hash_recovery_service.recover_wordlist_generator("5d41402abc4b2a76b9719d911017c592", "md5", wl)
    res = list(gen)
    
    assert len(res) == 1
    assert res[-1]["status"] == "NO_MATCH"

def test_verify_invalid_algorithm() -> None:
    res = hash_recovery_service.verify_candidate("abc", "fakealgo", "hello")
    assert res.status == "ERROR"


