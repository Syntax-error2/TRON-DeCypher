import sys
import os
import csv
import json
import base64
import zlib
import gzip
import hashlib
import urllib.parse
import html
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from app.decoders.core.registry import decoder_registry
from app.decoders.core.models import DecoderInput
from app.services.candidate_generation import CandidateGenerator, CandidateConfig
from app.services.hash_recovery import hash_recovery_service
from app.knowledge.flag_detection import flag_detection_service

results = []

def run_test(test_id, category, feature, input_val, expected_output, test_func):
    try:
        actual = test_func(input_val)
        passed = (actual == expected_output)
        status = "PASS" if passed else "FAIL"
        err = ""
        acc = 1.0 if passed else 0.0
    except Exception as e:
        actual = str(e)
        status = "FAIL"
        err = str(e)
        acc = 0.0
        passed = False
        
    res = {
        "TEST ID": test_id,
        "CATEGORY": category,
        "FEATURE": feature,
        "INPUT": str(input_val)[:50],
        "EXPECTED": str(expected_output)[:50],
        "ACTUAL": str(actual)[:50],
        "ACCURACY": acc,
        "STATUS": status,
        "ERROR": err,
        "ROOT CAUSE": "",
        "FIX": "",
        "REGRESSION TEST": ""
    }
    results.append(res)
    return passed

def test_decoder(decoder_name, input_val, params=None):
    decoder = decoder_registry.get_decoder(decoder_name)
    if not decoder:
        raise Exception(f"Decoder {decoder_name} not found")
    res = decoder.run(DecoderInput(text=input_val), params or {})
    if res.output_text:
        return res.output_text
    elif res.output_data:
        return res.output_data.decode('utf-8', errors='ignore')
    return ""

def b58encode(v: bytes) -> str:
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    p, acc = 0, 0
    for b in v:
        acc = acc * 256 + b
    res = []
    while acc > 0:
        acc, mod = divmod(acc, 58)
        res.append(alphabet[mod])
    for b in v:
        if b == 0: res.append(alphabet[0])
        else: break
    return ''.join(reversed(res))

# We'll run the QA script and collect results
print("QA runner ready")
# Tests to append

def run_all_qa():
    # Base64
    run_test("DEC-01", "Decoder", "Base64", 
             base64.b64encode(b"CTK{BASE64_TRON_2026}").decode(), 
             "CTK{BASE64_TRON_2026}", 
             lambda x: test_decoder("base64", x))
             
    # Base32
    run_test("DEC-02", "Decoder", "Base32", 
             base64.b32encode(b"CTK{BASE32_TEST}").decode(), 
             "CTK{BASE32_TEST}", 
             lambda x: test_decoder("base32", x))
             
    # Base58
    run_test("DEC-03", "Decoder", "Base58", 
             b58encode(b"CTK{BASE58_TEST}"), 
             "CTK{BASE58_TEST}", 
             lambda x: test_decoder("base58", x))
             
    # Base85
    run_test("DEC-04", "Decoder", "Base85", 
             base64.b85encode(b"CTK{BASE85_TEST}").decode(), 
             "CTK{BASE85_TEST}", 
             lambda x: test_decoder("base85", x))
             
    # Hex
    run_test("DEC-05", "Decoder", "Hex", 
             "43544b7b4845585f544553547d", 
             "CTK{HEX_TEST}", 
             lambda x: test_decoder("hex", x))
             
    # URL
    run_test("DEC-06", "Decoder", "URL", 
             "CTK%7BURL%5FTEST%7D", 
             "CTK{URL_TEST}", 
             lambda x: test_decoder("url", x))
             
    # HTML
    run_test("DEC-07", "Decoder", "HTML", 
             "&#67;&#84;&#75;&#123;&#72;&#84;&#77;&#76;&#125;", 
             "CTK{HTML}", 
             lambda x: test_decoder("html", x))
             
    # Unicode
    run_test("DEC-08", "Decoder", "Unicode", 
             "\u0043\u0054\u004b\u007b\u0055\u004e\u0049\u0043\u004f\u0044\u0045\u007d", 
             "CTK{UNICODE}", 
             lambda x: test_decoder("unicode", x))
             
    # Binary
    run_test("DEC-09", "Decoder", "Binary", 
             "01000011 01010100 01001011 01111011 01000010 01001001 01001110 01000001 01010010 01011001 01111101", 
             "CTK{BINARY}", 
             lambda x: test_decoder("binary", x))
             
    # Decimal
    run_test("DEC-10", "Decoder", "Decimal", 
             "67 84 75 123 68 69 67 73 77 65 76 125", 
             "CTK{DECIMAL}", 
             lambda x: test_decoder("decimal", x))
             
    # Octal
    run_test("DEC-11", "Decoder", "Octal", 
             "103 124 113 173 117 103 124 101 114 175", 
             "CTK{OCTAL}", 
             lambda x: test_decoder("octal", x))
             
    # ROT13
    run_test("DEC-12", "Decoder", "ROT13", 
             "PGX{URYYB}", 
             "CTK{HELLO}", 
             lambda x: test_decoder("rot13", x))
             
    # ROT47
    def rot47(s):
        out = []
        for c in s:
            if 33 <= ord(c) <= 126:
                out.append(chr(33 + ((ord(c) - 33 + 47) % 94)))
            else:
                out.append(c)
        return "".join(out)
    
    run_test("DEC-13", "Decoder", "ROT47", 
             rot47("CTK{ROT47_TEST}"), 
             "CTK{ROT47_TEST}", 
             lambda x: test_decoder("rot47", x))
             
    # Caesar
    run_test("DEC-14", "Decoder", "Caesar", 
             "KHOOR", 
             "HELLO", 
             lambda x: test_decoder("caesar", x, {"shift": 3}))
             
    # Atbash
    run_test("DEC-15", "Decoder", "Atbash", 
             "XGP{SVIIL}", 
             "CTK{HELLO}", 
             lambda x: test_decoder("atbash", x))
             
    # Morse
    run_test("DEC-16", "Decoder", "Morse", 
             "-.-. - -.- / .... . .-.. .-.. ---", 
             "CTK HELLO", 
             lambda x: test_decoder("morse", x))
             
    # A1Z26
    run_test("DEC-17", "Decoder", "A1Z26", 
             "3 20 11 8 5", 
             "CTKHE", 
             lambda x: test_decoder("a1z26", x))
             
    # Baconian
    def baconian_enc(s):
        # simple a=AAAAA, b=AAAAB...
        # Wait, the app probably has standard Baconian.
        return ""
        
    # Write to CSV
    with open('FINAL_QA_TEST_MATRIX.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

run_all_qa()
print(f"Ran {len(results)} tests.")
