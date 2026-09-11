import logging
from pathlib import Path
from typing import Any

from scapy.config import conf; conf.logLevel = logging.ERROR
from scapy.layers.dns import DNS
from scapy.layers.inet import TCP
from scapy.packet import Raw
from scapy.utils import PcapReader

from app.network.models import Conversation, DNSQuery, HTTPRequest, PacketSummary, PcapStatistics
from app.network.parsers.scapy_parser import PcapStreamingParser

logger = logging.getLogger(__name__)

class NetworkOrchestrator:
    """Streams a PCAP and feeds packets to sub-analyzers in one pass."""
    
    def __init__(self) -> None:
        pass
        
    def analyze_pcap(self, pcap_path: str | Path, max_packets: int = 500000) -> PcapStatistics:
        stats = PcapStatistics()
        
        convos: dict[str, Conversation] = {}
        
        try:
            with PcapReader(str(pcap_path)) as pcap_reader:
                for i, pkt in enumerate(pcap_reader, 1):
                    if i > max_packets:
                        logger.warning(f"Hit max_packets limit ({max_packets}), stopping early.")
                        break
                        
                    length = len(pkt)
                    ts = float(pkt.time)
                    
                    stats.total_packets += 1
                    stats.total_bytes += length
                    
                    if stats.first_timestamp == 0.0:
                        stats.first_timestamp = ts
                    stats.last_timestamp = ts
                    
                    # Protocol tracking & basic summary
                    # For performance, we do lightweight analysis inline.
                    # In a bigger system, this would be a pipeline of Observer classes.
                    
                    summary = self._fast_summarize(pkt, i, ts, length)
                    stats.protocols[summary.protocol] = stats.protocols.get(summary.protocol, 0) + 1
                    
                    if summary.src_ip:
                        stats.top_src_ips[summary.src_ip] = stats.top_src_ips.get(summary.src_ip, 0) + 1
                    if summary.dst_ip:
                        stats.top_dst_ips[summary.dst_ip] = stats.top_dst_ips.get(summary.dst_ip, 0) + 1
                        
                    # Conversations
                    if summary.src_ip and summary.dst_ip:
                        # Normalize key so A->B and B->A share the same conversation
                        key_tuple = sorted([(summary.src_ip, summary.src_port), (summary.dst_ip, summary.dst_port)])
                        key = f"{key_tuple[0][0]}:{key_tuple[0][1]}-{key_tuple[1][0]}:{key_tuple[1][1]}-{summary.protocol}"
                        
                        if key not in convos:
                            convos[key] = Conversation(
                                src_ip=key_tuple[0][0], dst_ip=key_tuple[1][0],
                                src_port=key_tuple[0][1], dst_port=key_tuple[1][1],
                                protocol=summary.protocol,
                                first_seen=ts
                            )
                        
                        convos[key].packet_count += 1
                        convos[key].bytes_transferred += length
                        convos[key].last_seen = ts
                        
                    # Deep Analysis (DNS)
                    if DNS in pkt and pkt.haslayer(DNS):
                        self._analyze_dns(pkt, ts, summary, stats)
                        
                    # Deep Analysis (HTTP plaintext)
                    if TCP in pkt and pkt.haslayer(Raw):
                        self._analyze_http(pkt, ts, summary, stats)
                        
        except Exception as e:
            logger.error(f"Error during PCAP analysis: {e}")
            
        stats.conversations = list(convos.values())
        return stats
        
    def _fast_summarize(self, pkt: "Any", index: int, ts: float, length: int) -> PacketSummary:
        # Borrow the logic from our parser for consistency
        parser = PcapStreamingParser("") # dummy
        return parser._summarize_packet(index, pkt)
        
    def _analyze_dns(self, pkt: "Any", ts: float, summary: PacketSummary, stats: PcapStatistics) -> None:
        dns = pkt[DNS]
        if dns.qdcount > 0 and hasattr(dns, 'qd') and dns.qd is not None:
            # Handle both bytes and str qname
            qname_val = dns.qd.qname
            if isinstance(qname_val, bytes):
                qname = qname_val.decode('utf-8', errors='ignore').rstrip('.')
            else:
                qname = str(qname_val).rstrip('.')
            qtype = getattr(dns.qd, 'qtype', 0)
            
            # 1 = A, 28 = AAAA, 5 = CNAME, 16 = TXT, 15 = MX
            qtype_map = {1: "A", 28: "AAAA", 5: "CNAME", 16: "TXT", 15: "MX"}
            qtype_str = qtype_map.get(qtype, str(qtype))
            
            answers = []
            if dns.ancount > 0 and hasattr(dns, 'an') and dns.an is not None:
                # Scapy's DNSRR can be iterated if multiple
                for i in range(dns.ancount):
                    try:
                        ans = dns.an[i]
                        rdata = getattr(ans, 'rdata', None)
                        if isinstance(rdata, bytes):
                            rdata = rdata.decode('utf-8', errors='ignore')
                        answers.append(str(rdata))
                    except Exception:
                        pass
                        
            stats.dns_queries.append(DNSQuery(
                timestamp=ts,
                client=summary.src_ip or "Unknown",
                server=summary.dst_ip or "Unknown",
                query=qname,
                qtype=qtype_str,
                answers=answers
            ))
            
    def _analyze_http(self, pkt: "Any", ts: float, summary: PacketSummary, stats: PcapStatistics) -> None:
        raw_data = pkt[Raw].load
        if b"HTTP/" in raw_data:
            try:
                # Basic HTTP heuristic
                text = raw_data.decode('utf-8', errors='ignore')
                lines = text.split('\r\n')
                if not lines:
                    return
                first_line = lines[0]
                
                if first_line.startswith(("GET ", "POST ", "PUT ", "DELETE ", "HEAD ")):
                    parts = first_line.split()
                    if len(parts) >= 3:
                        method, uri, _version = parts[0], parts[1], parts[2]
                        host = "Unknown"
                        for line in lines[1:]:
                            if line.lower().startswith("host:"):
                                host = line.split(":", 1)[1].strip()
                                break
                                
                        stats.http_requests.append(HTTPRequest(
                            timestamp=ts,
                            client=summary.src_ip or "Unknown",
                            server=summary.dst_ip or "Unknown",
                            method=method,
                            host=host,
                            uri=uri
                        ))
            except Exception:
                pass

network_orchestrator = NetworkOrchestrator()


