import logging

from scapy.config import conf; conf.logLevel = logging.ERROR
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether

# Scapy imports
from scapy.utils import PcapReader

from app.network.models import PacketSummary

logger = logging.getLogger(__name__)

class PcapStreamingParser:
    """Parses PCAP files efficiently using an iterator, bounding memory usage."""
    
    def __init__(self, pcap_path: str | Path):
        self.pcap_path = str(pcap_path)
        
    def iter_packets(self) -> Iterator[PacketSummary]:
        """Yields PacketSummary objects to avoid loading the full PCAP into memory."""
        try:
            with PcapReader(self.pcap_path) as pcap_reader:
                for i, pkt in enumerate(pcap_reader, 1):
                    yield self._summarize_packet(i, pkt)
        except Exception as e:
            logger.error(f"Failed to read PCAP {self.pcap_path}: {e}")
            
    def _summarize_packet(self, index: int, pkt: "Any") -> PacketSummary:
        summary = PacketSummary(
            packet_number=index,
            timestamp=float(pkt.time),
            length=len(pkt)
        )
        
        # L2
        if Ether in pkt:
            summary.src_mac = pkt[Ether].src
            summary.dst_mac = pkt[Ether].dst
            summary.protocol = "Ethernet"
            
        # L3
        if IP in pkt:
            summary.src_ip = pkt[IP].src
            summary.dst_ip = pkt[IP].dst
            summary.protocol = "IPv4"
        elif IPv6 in pkt:
            summary.src_ip = pkt[IPv6].src
            summary.dst_ip = pkt[IPv6].dst
            summary.protocol = "IPv6"
            
        # L4
        if TCP in pkt:
            summary.src_port = pkt[TCP].sport
            summary.dst_port = pkt[TCP].dport
            summary.protocol = "TCP"
            summary.info = f"{summary.src_port} -> {summary.dst_port} [flags: {pkt[TCP].flags}]"
        elif UDP in pkt:
            summary.src_port = pkt[UDP].sport
            summary.dst_port = pkt[UDP].dport
            summary.protocol = "UDP"
            summary.info = f"{summary.src_port} -> {summary.dst_port}"
        elif ICMP in pkt:
            summary.protocol = "ICMP"
            
        # Very basic application layer hints (will be done properly in analyzers)
        if summary.protocol in ("TCP", "UDP"):
            if summary.dst_port == 53 or summary.src_port == 53:
                summary.protocol = "DNS"
            elif summary.dst_port == 80 or summary.src_port == 80:
                summary.protocol = "HTTP"
            elif summary.dst_port == 443 or summary.src_port == 443:
                summary.protocol = "TLS/HTTPS"
                
        return summary


