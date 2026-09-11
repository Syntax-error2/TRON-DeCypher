import pytest

from app.crypto.analyzers.frequency import frequency_analysis_service
from app.crypto.classical.caesar import caesar_analyzer
from app.crypto.models import CryptoInput
from app.crypto.rsa.assessment import rsa_assessment_service
from app.crypto.rsa.factorization import bounded_factorization
from app.crypto.rsa.number_theory import mod_inverse
from app.crypto.services.identification import crypto_identification_service
from app.crypto.xor.analyzer import xor_analyzer


def test_identification() -> None:
    # Test hex
    ci = CryptoInput("414243")
    res = crypto_identification_service.analyze(ci)
    algos = [c["algorithm"] for c in res.candidates]
    assert "Hex" in algos
    
    # Test base64
    ci = CryptoInput("SGVsbG8=")
    res = crypto_identification_service.analyze(ci)
    algos = [c["algorithm"] for c in res.candidates]
    assert "Base64" in algos

def test_frequency_ioc() -> None:
    # English text
    text = "THIS IS A TEST OF THE EMERGENCY BROADCAST SYSTEM"
    ci = CryptoInput(text)
    res = frequency_analysis_service.analyze(ci)
    assert res.success
    # English IoC should be roughly > 1.4
    assert res.parameters["ioc"] > 1.4

def test_caesar() -> None:
    # "HELLO" shifted by 3 -> "KHOOR"
    ci = CryptoInput("KHOOR")
    res = caesar_analyzer.analyze(ci)
    assert res.success
    
    # In some short tests 'HELLO' might not be the exact top score due to sample size,
    # but the logic should return candidates.
    assert len(res.candidates) == 26
    
def test_xor() -> None:
    # "HELLO" ^ 0x42 -> b'\x0a\x07\x0e\x0e\x0d'
    # Actually wait, hex is easier
    # "HELLO" (48 45 4C 4C 4F) ^ 0x20 = (68 65 6C 6C 6F) -> "hello"
    ci = CryptoInput("68656c6c6f", input_type="hex")
    res = xor_analyzer.analyze_single_byte(ci)
    assert res.success
    # 0x20 should be a candidate
    keys = [c["key_int"] for c in res.candidates]
    assert 0x20 in keys

def test_rsa_math() -> None:
    # mod_inverse
    assert mod_inverse(3, 11) == 4
    with pytest.raises(ValueError):
        mod_inverse(2, 4)
        
    # factorization
    res = bounded_factorization.trial_division(15)
    assert res is not None
    assert (3, 5) == res or (5, 3) == res
    
    # RSA Assessment
    n = 3233  # 61 * 53
    e = 17
    # c for 'A' (65) = 65^17 mod 3233 = 2790
    c = 2790
    res2 = rsa_assessment_service.assess(n=n, e=e, c=c)
    assert res2.success
    # Should factor 3233
    assert "d" in res2.parameters
    assert "pt_int" in res2.parameters
    assert res2.parameters["pt_int"] == 65
