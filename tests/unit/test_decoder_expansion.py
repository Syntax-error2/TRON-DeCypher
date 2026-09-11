from app.decoders.core.models import DecoderInput
from app.decoders.encoding.base_ex_decoder import Base58Decoder, Base85Decoder
from app.decoders.encoding.compression import GzipDecoder, ZlibDecoder
from app.decoders.encoding.jwt_decoder import JwtDecoder
from app.decoders.numeric.numeric_ex_decoder import (
    BitwiseNotDecoder,
    ByteSwapDecoder,
    DecimalAsciiDecoder,
    OctalAsciiDecoder,
)
from app.decoders.text.text_ex_decoder import JsonEscapeDecoder, PunycodeDecoder
from app.services.hash_identification import hash_identification_service
from app.services.hashing_service import hashing_service


def test_hashing_service_basic() -> None:
    res = hashing_service.hash_bytes(b"Hello World", ["md5", "sha256", "crc32"])
    assert res["md5"] == "b10a8db164e0754105b7a99be72e3fe5"
    assert res["sha256"] == "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
    assert res["crc32"] == "4a17b156"

def test_hashing_service_algorithms() -> None:
    algos = hashing_service.get_supported_algorithms()
    assert "md5" in algos
    assert "sha1" in algos
    assert "sha512" in algos
    assert "crc32" in algos

def test_hash_identification() -> None:
    cands = hash_identification_service.identify("b10a8db164e0754105b7a99be72e3fe5")
    assert "MD5" in [c.algorithm.upper() for c in cands]
    
    cands_sha1 = hash_identification_service.identify("2ef7bde608ce5404e97d5f042f95f89f1c232871")
    assert "SHA1" in [c.algorithm.upper() for c in cands_sha1]

def test_base58_decoder() -> None:
    d = Base58Decoder()
    # Decode
    res = d.decode(DecoderInput(text="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"), {"mode": "decode"})
    assert res.success
    # Encode
    res_enc = d.decode(DecoderInput(data=res.output_data), {"mode": "encode"})
    assert res_enc.success
    
def test_base85_decoder() -> None:
    d = Base85Decoder()
    txt = b"hello world"
    res = d.decode(DecoderInput(data=txt), {"mode": "encode", "variant": "b85"})
    assert res.success
    res2 = d.decode(DecoderInput(data=res.output_data), {"mode": "decode", "variant": "b85"})
    assert res2.output_data == txt

def test_punycode_decoder() -> None:
    d = PunycodeDecoder()
    res = d.decode(DecoderInput(text="xn--mnchen-3ya.com"), {"mode": "decode"})
    assert res.success
    assert res.output_text == "münchen.com"

def test_json_escape_decoder() -> None:
    d = JsonEscapeDecoder()
    res = d.decode(DecoderInput(text="Hello\\nWorld"), {"mode": "decode"})
    assert res.success
    assert res.output_text == "Hello\nWorld"

def test_compression_decoders() -> None:
    g = GzipDecoder()
    z = ZlibDecoder()
    data = b"hello " * 100
    
    # Gzip
    res = g.decode(DecoderInput(data=data), {"mode": "compress"})
    res2 = g.decode(DecoderInput(data=res.output_data), {"mode": "decompress"})
    assert res2.output_data == data
    
    # Zlib
    res = z.decode(DecoderInput(data=data), {"mode": "compress"})
    res2 = z.decode(DecoderInput(data=res.output_data), {"mode": "decompress"})
    assert res2.output_data == data

def test_jwt_decoder() -> None:
    d = JwtDecoder()
    # Basic JWT without signature
    token = "eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
    res = d.decode(DecoderInput(text=token), {})
    assert res.success
    assert res.output_text is not None and "John Doe" in res.output_text
    
def test_numeric_ex_decoders() -> None:
    da = DecimalAsciiDecoder()
    res = da.decode(DecoderInput(text="72 101 108 108 111"), {"mode": "decode"})
    assert res.output_text == "Hello"
    
    oa = OctalAsciiDecoder()
    res2 = oa.decode(DecoderInput(text="110 145 154 154 157"), {"mode": "decode"})
    assert res2.output_text == "Hello"
    
    bnot = BitwiseNotDecoder()
    res3 = bnot.decode(DecoderInput(data=b"\x00\xFF"), {})
    assert res3.output_data == b"\xFF\x00"
    
    bswap = ByteSwapDecoder()
    res4 = bswap.decode(DecoderInput(data=b"\x01\x02\x03\x04"), {})
    assert res4.output_data == b"\x02\x01\x04\x03"


