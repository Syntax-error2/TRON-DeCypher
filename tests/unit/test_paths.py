from typing import Any

from app.core.paths import CASES_DIR, DATA_DIR


def test_paths_defined() -> None:
    assert DATA_DIR.name == "data"
    assert CASES_DIR.name == "cases"

def test_ensure_directories(tmp_path: Any, monkeypatch: Any) -> None:
    import app.core.paths
    monkeypatch.setattr(app.core.paths, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(app.core.paths, "CASES_DIR", tmp_path / "cases")
    monkeypatch.setattr(app.core.paths, "LOGS_DIR", tmp_path / "logs")
    monkeypatch.setattr(app.core.paths, "CONFIG_DIR", tmp_path / "config")
    monkeypatch.setattr(app.core.paths, "TOOLS_DIR", tmp_path / "tools")
    
    app.core.paths.ensure_directories()
    
    assert (tmp_path / "data").exists()
    assert (tmp_path / "cases").exists()
