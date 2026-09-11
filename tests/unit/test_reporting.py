import json
import os
import tempfile

from app.reporting.services.reporting_service import ReportingService


def test_reporting_service_masking() -> None:
    svc = ReportingService()
    
    mock_data = {
        "case": {"name": "Test Case"},
        "findings": [
            {"title": "Found Password", "description": "password: SuperSecret123!"}
        ]
    }
    
    masked = svc._mask_data(mock_data)
    
    assert masked["case"]["name"] == "Test Case"
    assert "SuperSecret123!" not in masked["findings"][0]["description"]
    assert "[REDACTED_PASSWORD]" in masked["findings"][0]["description"]

def test_json_export() -> None:
    ReportingService()
    mock_data = {"case": {"name": "Export Test"}}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        path = f.name
        
    try:
        from app.reporting.exporters.json_exporter import export_json
        export_json(mock_data, path)
        
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            
        assert loaded["case"]["name"] == "Export Test"
    finally:
        os.unlink(path)
