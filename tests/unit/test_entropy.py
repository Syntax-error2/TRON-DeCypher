from typing import Any

from app.analyzers.core.entropy_analyzer import EntropyAnalyzer


def test_entropy_analyzer(tmp_path: Any) -> None:
    f = tmp_path / "entropy_test.bin"
    # Create some highly repetitive data (low entropy)
    f.write_bytes(b"\x00" * 1000)
    
    analyzer = EntropyAnalyzer()
    result = analyzer.run(f, {})
    
    assert result.entropy == 0.0
    
    # Create random-ish data
    f.write_bytes(bytes(range(256)) * 4)
    result = analyzer.run(f, {})
    
    assert result.entropy > 7.9
