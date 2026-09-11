import os

from app.services.hash_recovery import hash_recovery_service
from app.services.image_analyzer import image_analyzer_service


def test_hash_automatic_recovery() -> None:
    # MD5 for 'hello' is 5d41402abc4b2a76b9719d911017c592
    target = '5d41402abc4b2a76b9719d911017c592'
    gen = hash_recovery_service.recover_automatic_generator(target, 'md5')
    results = list(gen)
    
    assert len(results) > 0
    assert any(r.get("status") == "RUNNING" for r in results)
    
    final_res = results[-1]
    assert final_res["status"] == "MATCH"
    assert final_res["candidate"] == "hello"
    
def test_image_analyzer() -> None:
    # Create a dummy PNG file
    path = "test_dummy.png"
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x01\x02\x03\x04")
        
    try:
        res = image_analyzer_service.analyze(path)
        assert res["format"] == "PNG"
        assert "sha256" in res
    finally:
        os.remove(path)

