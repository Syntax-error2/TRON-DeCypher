from typing import Any

from app.analyzers.core.string_extractor import StringExtractorAnalyzer


def test_string_extractor(tmp_path: Any) -> None:
    f = tmp_path / "strings.bin"
    data = b"\x00\x01\x02hello_world\x03\x04test_string\x00"
    f.write_bytes(data)
    
    analyzer = StringExtractorAnalyzer()
    results = analyzer.run(f, {"min_length": 4})
    
    assert len(results) == 2
    assert results[0].string == "hello_world"
    assert results[1].string == "test_string"
