import ipaddress
import re
import uuid

from app.osint.models import IOC, IOCType
from app.osint.normalization import ioc_normalization_service


class IOCExtractionService:
    """Extracts IOCs from text using regex and secondary validation."""
    
    # Regex patterns
    IPV4_PATTERN = re.compile(r'(?:\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')
    IPV6_PATTERN = re.compile(r'(?<![:.\w])(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}(?![:.\w])', re.IGNORECASE)
    # Simple domain regex
    DOMAIN_PATTERN = re.compile(r'(?:\b[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
    URL_PATTERN = re.compile(r'https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}(?:/[^ \n\r\t<>"\']*)?', re.IGNORECASE)
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    MAC_PATTERN = re.compile(r'(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})')
    
    # Broad hex pattern, will validate length later
    HEX_PATTERN = re.compile(r'\b[a-fA-F0-9]{32,128}\b')

    def extract(self, text: str, case_id: str) -> list[IOC]:
        raw_matches: list[tuple[IOCType, str]] = []
        
        # IPv4
        for m in self.IPV4_PATTERN.findall(text):
            if self._validate_ipv4(m):
                raw_matches.append((IOCType.IPV4, m))
                
        # IPv6
        for m in self.IPV6_PATTERN.findall(text):
            if self._validate_ipv6(m):
                raw_matches.append((IOCType.IPV6, m))
                
        # URLs
        for m in self.URL_PATTERN.findall(text):
            raw_matches.append((IOCType.URL, m))
            
        # Emails
        for m in self.EMAIL_PATTERN.findall(text):
            raw_matches.append((IOCType.EMAIL, m))
            
        # Domains (only keep if not part of email or URL to avoid double counting, though strict deduplication handles it)
        for m in self.DOMAIN_PATTERN.findall(text):
            if not self._is_file_extension(m) and m.lower() != "localhost":
                raw_matches.append((IOCType.DOMAIN, m))
                
        # MAC
        for m in self.MAC_PATTERN.findall(text):
            raw_matches.append((IOCType.MAC, m))
            
        # Hashes
        for m in self.HEX_PATTERN.findall(text):
            length = len(m)
            if length == 32:
                raw_matches.append((IOCType.MD5, m))
            elif length == 40:
                raw_matches.append((IOCType.SHA1, m))
            elif length == 64:
                raw_matches.append((IOCType.SHA256, m))
            elif length == 128:
                raw_matches.append((IOCType.SHA512, m))
                
        # Normalize and Deduplicate logic (In-memory representation before saving)
        # Usually, saving to DB handles deduplication by normalized_value, but we can do it here for the batch.
        iocs: dict[str, IOC] = {}
        for ioc_type, val in raw_matches:
            norm = ioc_normalization_service.normalize(ioc_type, val)
            key = f"{ioc_type.value}_{norm}"
            if key not in iocs:
                iocs[key] = IOC(
                    id=f"ioc_{uuid.uuid4().hex[:12]}",
                    case_id=case_id,
                    ioc_type=ioc_type,
                    value=val,
                    normalized_value=norm
                )
                
        return list(iocs.values())

    def _validate_ipv4(self, ip_str: str) -> bool:
        try:
            ipaddress.IPv4Address(ip_str)
            return True
        except ipaddress.AddressValueError:
            return False

    def _validate_ipv6(self, ip_str: str) -> bool:
        try:
            ipaddress.IPv6Address(ip_str)
            return True
        except ipaddress.AddressValueError:
            return False
            
    def _is_file_extension(self, text: str) -> bool:
        common_exts = {".exe", ".dll", ".txt", ".png", ".jpg", ".pdf", ".zip", ".tar", ".gz", ".doc", ".docx"}
        return any(text.lower().endswith(ext) for ext in common_exts)

ioc_extraction_service = IOCExtractionService()
