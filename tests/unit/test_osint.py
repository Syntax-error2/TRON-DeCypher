from app.osint.extraction import ioc_extraction_service
from app.osint.models import IOCType
from app.osint.normalization import ioc_normalization_service


def test_ipv4_validation() -> None:
    # Valid
    iocs = ioc_extraction_service.extract("The attacker IP is 192.168.1.10.", case_id="test")
    assert len(iocs) == 1
    assert iocs[0].ioc_type == IOCType.IPV4
    
    # Invalid (regex matches structure, validation should reject)
    iocs_invalid = ioc_extraction_service.extract("The attacker IP is 999.999.999.999.", case_id="test")
    assert len(iocs_invalid) == 0

def test_normalization() -> None:
    norm1 = ioc_normalization_service.normalize(IOCType.DOMAIN, "Example.COM")
    assert norm1 == "example.com"
    
    norm2 = ioc_normalization_service.normalize(IOCType.DOMAIN, "http://malicious.org/")
    assert norm2 == "malicious.org"
    
    norm3 = ioc_normalization_service.normalize(IOCType.EMAIL, "User@Test.Com")
    assert norm3 == "user@test.com"

def test_hash_extraction() -> None:
    text = "Found MD5: d41d8cd98f00b204e9800998ecf8427e and SHA1: da39a3ee5e6b4b0d3255bfef95601890afd80709"
    iocs = ioc_extraction_service.extract(text, case_id="test")
    assert len(iocs) == 2
    types = {ioc.ioc_type for ioc in iocs}
    assert IOCType.MD5 in types
    assert IOCType.SHA1 in types

def test_mac_extraction() -> None:
    text = "The device MAC was 00:1A:2B:3C:4D:5E."
    iocs = ioc_extraction_service.extract(text, case_id="test")
    assert len(iocs) == 1
    assert iocs[0].ioc_type == IOCType.MAC
    assert iocs[0].value == "00:1A:2B:3C:4D:5E"
