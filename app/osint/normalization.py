from urllib.parse import urlparse

from app.osint.models import IOCType


class IOCNormalizationService:
    """Normalizes IOCs for deduplication and consistent storage."""
    
    def normalize(self, ioc_type: IOCType, value: str) -> str:
        val = value.strip()
        
        if ioc_type == IOCType.DOMAIN:
            # Lowercase and remove trailing dots
            val = val.lower().rstrip('.')
            # Remove scheme if someone mistakenly passed a URL as a domain
            if "://" in val:
                val = urlparse(val).hostname or val
                
        elif ioc_type == IOCType.EMAIL:
            val = val.lower()
            
        elif ioc_type == IOCType.URL:
            # We don't lowercase the whole URL, just the scheme and netloc if possible,
            # but for simple normalization we often just trim and rely on exact match.
            # To be safe and preserve original intention, we strip whitespace.
            # A full canonicalization could be done, but keeping it simple.
            pass
            
        elif ioc_type in [IOCType.MD5, IOCType.SHA1, IOCType.SHA256, IOCType.SHA512]:
            val = val.lower()
            
        elif ioc_type == IOCType.MAC:
            # Normalize to lowercase and remove separators
            val = val.lower().replace(":", "").replace("-", "")
            
        elif ioc_type in [IOCType.IPV4, IOCType.IPV6]:
            # Simple trim, advanced normalization (like compressing IPv6) can be added later
            val = val.lower()
            
        return val

ioc_normalization_service = IOCNormalizationService()
