from typing import Any

from app.models.artifact import Artifact
from app.services.triage_service import triage_service


def test_run_triage(tmp_path: Any) -> None:
    f = tmp_path / "test.txt"
    f.write_text("Hello World! This is a test file for triage.", encoding="utf-8")
    
    artifact = Artifact(
        id="art_1",
        case_id="case_1",
        filename="test.txt",
        original_path=str(f),
        stored_path=str(f),
        size=44
    )
    
    result = triage_service.run_triage(artifact)
    
    assert result.artifact.id == "art_1"
    assert "md5" in result.hashes
    assert len(result.strings) > 0
    assert result.entropy is not None
    assert result.entropy.entropy > 0.0
