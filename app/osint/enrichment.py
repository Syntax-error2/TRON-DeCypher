import logging

from app.osint.models import IOC, IntelResult, IOCType
from app.osint.providers.adapters import AVAILABLE_PROVIDERS

logger = logging.getLogger(__name__)

class IOCEnrichmentService:
    """Orchestrates enrichment, checking caches and offline mode."""
    
    def __init__(self) -> None:
        self.offline_mode = True # Default to secure offline mode
        
    def enrich_ioc(self, ioc: IOC) -> list[IntelResult]:
        """Runs external or cached lookups for a given IOC."""
        results = []
        
        # In a real database scenario, we'd check SQLite cache first.
        # For phase 5, we simulate the provider response (which might return cached/stubbed data).
        
        for provider in AVAILABLE_PROVIDERS:
            if not provider.is_configured() and not self.offline_mode:
                continue
                
            try:
                res = None
                if ioc.ioc_type in [IOCType.IPV4, IOCType.IPV6]:
                    res = provider.lookup_ip(ioc)
                elif ioc.ioc_type == IOCType.DOMAIN:
                    res = provider.lookup_domain(ioc)
                elif ioc.ioc_type == IOCType.URL:
                    res = provider.lookup_url(ioc)
                elif ioc.ioc_type in [IOCType.MD5, IOCType.SHA1, IOCType.SHA256, IOCType.SHA512]:
                    res = provider.lookup_hash(ioc)
                    
                if res:
                    results.append(res)
            except Exception as e:
                logger.error(f"Provider {provider.name()} failed: {e}")
                
        return results

ioc_enrichment_service = IOCEnrichmentService()
