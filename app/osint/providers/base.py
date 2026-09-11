from abc import ABC, abstractmethod

from app.osint.models import IOC, IntelResult


class ThreatIntelProvider(ABC):
    
    @abstractmethod
    def name(self) -> str:
        """Name of the provider."""
        
    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the provider has necessary keys/config."""
        
    @abstractmethod
    def lookup_ip(self, ioc: IOC) -> IntelResult | None:
        pass
        
    @abstractmethod
    def lookup_domain(self, ioc: IOC) -> IntelResult | None:
        pass
        
    @abstractmethod
    def lookup_url(self, ioc: IOC) -> IntelResult | None:
        pass
        
    @abstractmethod
    def lookup_hash(self, ioc: IOC) -> IntelResult | None:
        pass
