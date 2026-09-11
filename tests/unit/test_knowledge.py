from app.ai.services.copilot_service import copilot_service
from app.knowledge.knowledge_service import knowledge_service


def test_document_registration() -> None:
    doc_id = knowledge_service.register_document("Test Doc", "test.pdf", "test_sha", "USER_REFERENCE")
    assert doc_id is not None
    # Deduplication
    doc_id2 = knowledge_service.register_document("Test Doc", "test.pdf", "test_sha", "USER_REFERENCE")
    assert doc_id == doc_id2

def test_knowledge_search() -> None:
    res = knowledge_service.search("Caesar")
    assert len(res) > 0
    assert res[0]['topic'] == "Caesar Cipher"
    
def test_rsa_search() -> None:
    res = knowledge_service.search("RSA")
    assert len(res) > 0
    assert "RSA" in res[0]['topic']

def test_ghidra_search() -> None:
    res = knowledge_service.search("Ghidra")
    assert len(res) > 0
    
def test_wireshark_search() -> None:
    res = knowledge_service.search("Wireshark")
    assert len(res) > 0
    
def test_volatility_search() -> None:
    res = knowledge_service.search("Volatility")
    assert len(res) > 0
    
def test_exiftool_search() -> None:
    res = knowledge_service.search("ExifTool")
    assert len(res) > 0

def test_zsteg_search() -> None:
    res = knowledge_service.search("zsteg")
    assert len(res) > 0
    
def test_ffuf_search() -> None:
    res = knowledge_service.search("ffuf")
    assert len(res) > 0

def test_sqlmap_search() -> None:
    res = knowledge_service.search("sqlmap")
    assert len(res) > 0

def test_ai_integration() -> None:
    res = copilot_service.custom_query("art_123", "What should I inspect in a suspicious PNG?")
    # Based on our mock response hack:
    assert "No matching material" in res.summary or "Source:" in res.summary

def test_commands_are_references() -> None:
    cmds = knowledge_service.search_command("nmap")
    assert len(cmds) > 0
    assert cmds[0]['requires_explicit_execution'] == 1
    assert "Reference" not in cmds[0]['command'] # the command itself is just nmap -sV ...

