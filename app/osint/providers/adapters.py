import os
import uuid

from app.osint.models import IOC, IntelResult
from app.osint.providers.base import ThreatIntelProvider


class VirusTotalProvider(ThreatIntelProvider):
    def name(self) -> str:
        return "VirusTotal"
        
    def is_configured(self) -> bool:
        return bool(os.environ.get("VT_API_KEY"))
        
    def lookup_ip(self, ioc: IOC) -> IntelResult | None:
        return None
        
    def lookup_domain(self, ioc: IOC) -> IntelResult | None:
        # Stub for offline safety
        return IntelResult(
            id=f"ir_{uuid.uuid4().hex[:12]}",
            ioc_id=ioc.id,
            provider=self.name(),
            response_summary="VirusTotal lookup simulated (Offline/Unconfigured)"
        )
        
    def lookup_url(self, ioc: IOC) -> IntelResult | None:
        return None
        
    def lookup_hash(self, ioc: IOC) -> IntelResult | None:
        return IntelResult(
            id=f"ir_{uuid.uuid4().hex[:12]}",
            ioc_id=ioc.id,
            provider=self.name(),
            response_summary="VirusTotal hash lookup simulated (Offline)"
        )

class AbuseIPDBProvider(ThreatIntelProvider):
    def name(self) -> str:
        return "AbuseIPDB"
        
    def is_configured(self) -> bool:
        return bool(os.environ.get("ABUSEIPDB_API_KEY"))
        
    def lookup_ip(self, ioc: IOC) -> IntelResult | None:
        return IntelResult(
            id=f"ir_{uuid.uuid4().hex[:12]}",
            ioc_id=ioc.id,
            provider=self.name(),
            response_summary="AbuseIPDB lookup simulated (Offline)"
        )
        
    def lookup_domain(self, ioc: IOC) -> IntelResult | None:
        return None
        
    def lookup_url(self, ioc: IOC) -> IntelResult | None:
        return None
        
    def lookup_hash(self, ioc: IOC) -> IntelResult | None:
        return None

# Register configured providers
AVAILABLE_PROVIDERS = [
    VirusTotalProvider(),
    AbuseIPDBProvider()
]
