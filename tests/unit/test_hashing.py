from typing import Any

from app.services.hashing_service import hashing_service


def test_hash_bytes() -> None:
    data = b"test string"
    hashes = hashing_service.hash_bytes(data, ["md5", "sha1", "sha256"])
    
    assert hashes["md5"] == "6f8db599de986fab7a21625b7916589c"
    assert hashes["sha256"] == "d5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b"

def test_hash_file(tmp_path: Any) -> None:
    f = tmp_path / "test.txt"
    f.write_bytes(b"test string")
    
    hashes = hashing_service.hash_file(f, ["md5", "sha256"])
    assert hashes["md5"] == "6f8db599de986fab7a21625b7916589c"
    assert hashes["sha256"] == "d5579c46dfcc7f18207013e65b44e4cb4e2c2298f4ac457ba8f82743f31e930b"
