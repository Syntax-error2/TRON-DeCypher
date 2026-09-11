from app.services.tool_service import ToolService


def test_tool_service_initialization() -> None:
    service = ToolService()
    service.scan_for_tools()
    
    # We should have builtins, python packages, and executables
    assert len(service.tools) > 10
    assert "File Hashing" in service.tools
    assert "PySide6" in service.tools
    assert "Wireshark" in service.tools
