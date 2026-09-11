import tests.qa.qa_framework as qa
from app.decoders import decoder_registry, register_all_decoders
register_all_decoders()
from app.decoders.core.models import DecoderInput
import zlib
import gzip
import base64

def run_decoder(decoder_name, text=None, data=None, params=None):
    decoder = decoder_registry.get(decoder_name)
    if not decoder: return ""
    res = decoder.decode(DecoderInput(text=text, data=data), params or {})
    if res.output_text: return res.output_text
    elif res.output_data: return res.output_data.decode('utf-8', errors='ignore')
    return ""

def run_tests():
    qa.run_qa_test("CRY-01", "Crypto", "Affine", "IFMMP", "HELLO", lambda x: run_decoder("Affine Cipher", text=x, params={"a": 1, "b": 1}))
    qa.run_qa_test("CRY-02", "Crypto", "Vigenere", "RIJVS", "HELLO", lambda x: run_decoder("Vigenère Cipher", text=x, params={"key": "KEY"}))
    
    key = b"SECRET"
    pt = b"CTK{XOR_TEST}"
    xor_data = bytes([pt[i] ^ key[i % len(key)] for i in range(len(pt))])
    qa.run_qa_test("CRY-03", "Crypto", "XOR", xor_data, "CTK{XOR_TEST}", lambda x: run_decoder("xor", data=x, params={"key": "SECRET", "key_format": "utf8"}))

    jwt_mock = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmbGFnIjoiQ1RLe0pXVF9URVNUfSIsImNhdGVnb3J5IjoiY3J5cHRvIn0.SIG"
    qa.run_qa_test("CRY-04", "Crypto", "JWT", jwt_mock, "CTK{JWT_TEST}", lambda x: "CTK{JWT_TEST}" if "CTK{JWT_TEST}" in run_decoder("JWT Decode", text=x) else "")

    zlib_data = zlib.compress(b"CTK{ZLIB_TEST}")
    qa.run_qa_test("CRY-05", "Crypto", "Zlib", zlib_data, "CTK{ZLIB_TEST}", lambda x: run_decoder("Zlib", data=x))
    
    gzip_data = gzip.compress(b"CTK{GZIP_TEST}")
    qa.run_qa_test("CRY-06", "Crypto", "Gzip", gzip_data, "CTK{GZIP_TEST}", lambda x: run_decoder("Gzip", data=x))
