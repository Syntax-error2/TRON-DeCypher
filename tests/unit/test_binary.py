from app.binary.analyzers.api_classification import api_classification_service
from app.binary.integrations.tool_registry import binary_tool_registry
from app.binary.integrations.yara_foundation import yara_foundation_service
from app.binary.parsers.identification import binary_identification_analyzer


def test_binary_identification() -> None:
    assert binary_identification_analyzer.identify(b'\x7fELF') == "ELF"
    assert binary_identification_analyzer.identify(b'MZ\x90\x00') == "PE"
    assert binary_identification_analyzer.identify(b'\xce\xfa\xed\xfe') == "Mach-O"
    assert binary_identification_analyzer.identify(b'\xca\xfe\xba\xbe') == "Mach-O"
    assert binary_identification_analyzer.identify(b'Some random text') == "Unknown"
    
def test_api_classification() -> None:
    assert api_classification_service.classify("VirtualAllocEx") == "Memory"
    assert api_classification_service.classify("CreateFileW") == "File I/O"
    assert api_classification_service.classify("wsastartup") == "Networking"
    assert api_classification_service.classify("CheckRemoteDebuggerPresent") == "Debugging"
    assert api_classification_service.classify("SomeUnknownFunction") == "Standard"
    
def test_yara_foundation() -> None:
    # Just checking the stub doesn't crash
    if yara_foundation_service.is_available():
        # yara-python is installed in the test environment, so it will return True
        pass
    assert isinstance(yara_foundation_service.is_available(), bool)
    
def test_tool_registry() -> None:
    tools = binary_tool_registry.check_tools()
    assert "ghidra" in tools
    assert "gdb" in tools
    assert "radare2" in tools
    assert "rizin" in tools
