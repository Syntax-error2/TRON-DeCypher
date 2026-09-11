import base64
import urllib.parse
import binascii

import tests.qa.qa_framework as qa
from app.decoders import register_all_decoders, decoder_registry
from app.decoders.core.models import DecoderInput

register_all_decoders()

def run_decoder(decoder_name, text, params=None):
    decoder = decoder_registry.get(decoder_name)
    if not decoder:
        raise Exception(f"Decoder {decoder_name} not found")
    res = decoder.decode(DecoderInput(text=text), params or {})
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

def rot47(s):
    out = []
    for c in s:
        if 33 <= ord(c) <= 126:
            out.append(chr(33 + ((ord(c) - 33 + 47) % 94)))
        else:
            out.append(c)
    return "".join(out)

def run_tests():
    qa.run_qa_test("DEC-01", "Decoder", "Base64", base64.b64encode(b"CTK{BASE64_TRON_2026}").decode(), "CTK{BASE64_TRON_2026}", lambda x: run_decoder("base64", x))
    qa.run_qa_test("DEC-02", "Decoder", "Base32", base64.b32encode(b"CTK{BASE32_TEST}").decode(), "CTK{BASE32_TEST}", lambda x: run_decoder("base32", x))
    qa.run_qa_test("DEC-03", "Decoder", "Base58", b58encode(b"CTK{BASE58_TEST}"), "CTK{BASE58_TEST}", lambda x: run_decoder("Base58", x))
    qa.run_qa_test("DEC-04", "Decoder", "Base85", base64.b85encode(b"CTK{BASE85_TEST}").decode(), "CTK{BASE85_TEST}", lambda x: run_decoder("Base85 / ASCII85", x))
    qa.run_qa_test("DEC-05", "Decoder", "Hex", binascii.hexlify(b"CTK{HEX_TEST}").decode(), "CTK{HEX_TEST}", lambda x: run_decoder("hex", x))
    qa.run_qa_test("DEC-06", "Decoder", "URL", urllib.parse.quote("CTK{URL_TEST}"), "CTK{URL_TEST}", lambda x: run_decoder("url", x))
    qa.run_qa_test("DEC-07", "Decoder", "HTML Entities", "&#67;&#84;&#75;&#123;&#72;&#84;&#77;&#76;&#125;", "CTK{HTML}", lambda x: run_decoder("html", x))
    qa.run_qa_test("DEC-08", "Decoder", "Unicode Escapes", "\u0043\u0054\u004b\u007b\u0055\u004e\u0049\u0043\u004f\u0044\u0045\u007d", "CTK{UNICODE}", lambda x: run_decoder("unicode_escape", x))
    qa.run_qa_test("DEC-09", "Decoder", "Binary", "01000011 01010100 01001011 01111011 01000010 01001001 01001110 01000001 01010010 01011001 01111101", "CTK{BINARY}", lambda x: run_decoder("binary", x))
    qa.run_qa_test("DEC-10", "Decoder", "Decimal", "67 84 75 123 68 69 67 73 77 65 76 125", "CTK{DECIMAL}", lambda x: run_decoder("Decimal ASCII", x))
    qa.run_qa_test("DEC-11", "Decoder", "Octal", "103 124 113 173 117 103 124 101 114 175", "CTK{OCTAL}", lambda x: run_decoder("Octal ASCII", x))
    qa.run_qa_test("DEC-12", "Decoder", "ROT13", "PGX{URYYB}", "CTK{HELLO}", lambda x: run_decoder("ROT", x))
    qa.run_qa_test("DEC-13", "Decoder", "ROT47", rot47("CTK{ROT47_TEST}"), "CTK{ROT47_TEST}", lambda x: run_decoder("ROT", x, {"variant": "rot47"}))
    qa.run_qa_test("DEC-14", "Decoder", "Caesar", "KHOOR", "HELLO", lambda x: run_decoder("Caesar Cipher", x, {"shift": 3}))
    qa.run_qa_test("DEC-15", "Decoder", "Atbash", "XGP{SVOOL}", "CTK{HELLO}", lambda x: run_decoder("Atbash Cipher", x))
    qa.run_qa_test("DEC-16", "Decoder", "Morse", "-.-. - -.- / .... . .-.. .-.. ---", "CTK HELLO", lambda x: run_decoder("Morse Code", x))
    qa.run_qa_test("DEC-17", "Decoder", "A1Z26", "3 20 11 8 5", "CTKHE", lambda x: run_decoder("A1Z26 Cipher", x))
    
    # Test Baconian
    # Bacon encoding standard: A=AAAAA, B=AAAAB, C=AAABA ...
    # CTK = AABAA BAABA ABABA
    qa.run_qa_test("DEC-18", "Decoder", "Baconian", "AAABA BAABB ABABA", "CTK", lambda x: run_decoder("Bacon Cipher", x))

