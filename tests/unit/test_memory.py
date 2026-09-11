from app.memory.analyzers.injection_analyzer import injection_analyzer
from app.memory.analyzers.memory_identification import memory_identification_analyzer
from app.memory.models import MemoryAnalysisResult
from app.memory.parsers.volatility_parser import volatility_parser


def test_volatility_pslist_parser() -> None:
    res = MemoryAnalysisResult()
    data = [
        {"PID": 4, "PPID": 0, "ImageFileName": "System", "CreateTime": "2023-01-01"},
        {"PID": 1234, "PPID": 4, "ImageFileName": "svchost.exe"}
    ]
    volatility_parser.parse_pslist(data, res)
    assert len(res.processes) == 2
    assert res.processes[0].name == "System"
    assert res.processes[1].pid == 1234
    
def test_volatility_netscan_parser() -> None:
    res = MemoryAnalysisResult()
    data = [
        {"PID": 1234, "Owner": "svchost.exe", "Protocol": "TCPv4", "LocalAddr": "10.0.0.1", "LocalPort": 443, "ForeignAddr": "192.168.1.1", "ForeignPort": 50000, "State": "ESTABLISHED"}
    ]
    volatility_parser.parse_netscan(data, res)
    assert len(res.connections) == 1
    assert res.connections[0].source_ip == "10.0.0.1"
    
def test_injection_analyzer() -> None:
    res = MemoryAnalysisResult()
    # Add a suspicious svchost
    data = [{"PID": 9999, "PPID": 100, "ImageFileName": "svch0st.exe"}]
    volatility_parser.parse_pslist(data, res)
    
    # Add a suspicious module
    res.modules.append(
        __import__('app.memory.models', fromlist=['MemoryModule']).MemoryModule(
            process_name="Test", pid=100, name="malware.dll", path="C:\\Users\\Temp\\malware.dll", base_address="0x1000", size="1024"
        )
    )
    
    injection_analyzer.analyze(res)
    assert len(res.findings) >= 2
    
    svchost_finding = next((f for f in res.findings if "svch0st" in f.description), None)
    assert svchost_finding is not None
    assert svchost_finding.severity == "HIGH"
    
def test_memory_identification() -> None:
    res = MemoryAnalysisResult()
    # test dummy file that doesn't exist
    memory_identification_analyzer.analyze("does_not_exist.raw", res)
    assert res.os_hint == "Unknown"
    
    # We will assume if a file existed with "PAGE" it would be identified as Windows, 
    # but we won't create a temp file here to keep it simple, since the method checks os.path.exists
