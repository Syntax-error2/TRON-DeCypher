from pathlib import Path
from typing import Any

from app.services.artifact_service import artifact_service
from app.services.case_service import case_service


def test_ingest_file(tmp_path: Any) -> None:
    # Set cases dir to temp
    case_service.cases_dir = tmp_path / "cases"
    
    # Create case
    case = case_service.create_case("Ingest_Test")
    
    # Create dummy file
    dummy_file = tmp_path / "malware.exe"
    dummy_file.write_bytes(b"MZ\x90\x00\x03\x00\x00\x00" + b"A"*100)
    
    # Ingest
    artifact = artifact_service.ingest_file(case.id, dummy_file)
    
    assert artifact.case_id == case.id
    assert artifact.filename == "malware.exe"
    assert artifact.size == 108
    assert Path(artifact.stored_path).exists()
    assert Path(artifact.stored_path).name.startswith("malware")
    assert artifact.md5 is not None
    assert artifact.sha256 is not None
