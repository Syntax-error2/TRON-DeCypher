from pathlib import Path

from app.forensics.analyzers.embedded import EmbeddedDataAnalyzer
from app.forensics.analyzers.metadata import MetadataAnalyzer
from app.forensics.analyzers.signature import FileSignatureAnalyzer
from app.forensics.services.archive_service import archive_service


def test_signature_analyzer(tmp_path: Path) -> None:
    analyzer = FileSignatureAnalyzer()
    
    test_file = tmp_path / "test.png"
    test_file.write_bytes(b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' + b'\x00' * 50)
    
    matches = analyzer.analyze(test_file)
    assert len(matches) > 0
    assert matches[0].detected_type == "PNG"
    
    mismatch = analyzer.check_mismatch("test.jpg", matches)
    assert mismatch is not None
    assert "does not match" in mismatch

def test_embedded_analyzer(tmp_path: Path) -> None:
    analyzer = EmbeddedDataAnalyzer()
    
    # PNG with appended ZIP
    test_file = tmp_path / "test.png"
    data = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' + b'mock_png_data' + b'\x49\x45\x4E\x44\xAE\x42\x60\x82' + b'PK\x03\x04mock_zip_data'
    test_file.write_bytes(data)
    
    # Check appended data
    appended_offset = analyzer.check_appended_data(test_file, "PNG")
    assert appended_offset is not None
    
    # Check embedded signatures
    embedded = analyzer.analyze_embedded_signatures(test_file)
    assert len(embedded) > 0
    assert embedded[0].detected_type == "ZIP"

def test_metadata_analyzer(tmp_path: Path) -> None:
    analyzer = MetadataAnalyzer()
    
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")
    
    meta = analyzer.analyze(test_file)
    assert meta["size"] == 5
    assert meta["extension"] == ".txt"

def test_archive_service_safety() -> None:
    assert archive_service.is_safe_path("safe_file.txt")
    assert archive_service.is_safe_path("folder/file.png")
    assert not archive_service.is_safe_path("../etc/passwd")
    assert not archive_service.is_safe_path("/absolute/path.sh")
