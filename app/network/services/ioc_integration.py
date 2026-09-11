import logging

from app.network.models import PcapStatistics
from app.osint.extraction import ioc_extraction_service
from app.osint.models import IOC

logger = logging.getLogger(__name__)

class NetworkIOCIntegrationService:
    """Extracts IOCs from network statistics and forwards them to Phase 5 OSINT."""
    
    def extract_from_stats(self, stats: PcapStatistics, case_id: str) -> list[IOC]:
        """Scans DNS queries, HTTP hosts, and top IPs for IOCs."""
        
        # We consolidate texts to scan via the existing regex engine.
        text_corpus = []
        
        for ip in stats.top_src_ips:
            text_corpus.append(ip)
        for ip in stats.top_dst_ips:
            text_corpus.append(ip)
            
        for dns in stats.dns_queries:
            text_corpus.append(dns.query)
            for ans in dns.answers:
                text_corpus.append(ans)
                
        for http in stats.http_requests:
            text_corpus.append(http.host)
            text_corpus.append(f"http://{http.host}{http.uri}")
            
        combined_text = "\n".join(text_corpus)
        
        # Delegate to Phase 5
        iocs = ioc_extraction_service.extract(combined_text, case_id=case_id)
        logger.info(f"Extracted {len(iocs)} IOCs from Network statistics.")
        return iocs

network_ioc_integration = NetworkIOCIntegrationService()
