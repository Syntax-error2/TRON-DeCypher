from app.decoders.classical.affine import AffineDecoder
from app.decoders.classical.atbash_decoder import AtbashDecoder
from app.decoders.classical.baconian import BaconianDecoder
from app.decoders.classical.caesar import CaesarDecoder
from app.decoders.classical.hill import HillDecoder
from app.decoders.classical.morse_decoder import MorseDecoder
from app.decoders.classical.playfair import PlayfairDecoder
from app.decoders.classical.polybius_based import A1Z26Decoder
from app.decoders.classical.rot_decoder import RotDecoder
from app.decoders.classical.vigenere import VigenereDecoder
from app.decoders.core.models import DecoderInput


def test_caesar() -> None:
    decoder = CaesarDecoder()
    res = decoder.run(DecoderInput(text="KHOOR"), {"shift": 3})
    assert res.success
    assert res.output_text == "HELLO"
    
def test_caesar_auto_crack() -> None:
    decoder = CaesarDecoder()
    res = decoder.run(DecoderInput(text="KHOOR"), {"auto_crack": True})
    assert res.success
    assert res.output_text == "HELLO"
    assert res.metadata["best_shift"] == 3
    
def test_rot_variants() -> None:
    decoder = RotDecoder()
    res = decoder.run(DecoderInput(text="URYYB"), {"variant": "rot13"})
    assert res.success
    assert res.output_text == "HELLO"
    
    # "HELLO" rot47 is "wt{{~"
    res47 = decoder.run(DecoderInput(text="wt{{~"), {"variant": "rot47"})
    assert res47.output_text == "HELLO"
    
def test_atbash() -> None:
    decoder = AtbashDecoder()
    res = decoder.run(DecoderInput(text="SVOOL"), {})
    assert res.output_text == "HELLO"

def test_morse() -> None:
    decoder = MorseDecoder()
    res = decoder.run(DecoderInput(text=".... . .-.. .-.. ---"), {"mode": "decode"})
    assert res.output_text == "HELLO"
    
def test_a1z26() -> None:
    decoder = A1Z26Decoder()
    res = decoder.run(DecoderInput(text="8 5 12 12 15"), {"mode": "decode"})
    assert res.output_text == "HELLO"

def test_baconian() -> None:
    decoder = BaconianDecoder()
    res = decoder.run(DecoderInput(text="AABAA AABAA"), {"mode": "decode", "alphabet": "standard"})
    assert "E" in res.output_text

def test_vigenere() -> None:
    decoder = VigenereDecoder()
    res = decoder.run(DecoderInput(text="HELLO"), {"mode": "encrypt", "key": "KEY"})
    assert res.output_text == "RIJVS"
    res_dec = decoder.run(DecoderInput(text="RIJVS"), {"mode": "decrypt", "key": "KEY"})
    assert res_dec.output_text == "HELLO"
    
def test_affine() -> None:
    decoder = AffineDecoder()
    res = decoder.run(DecoderInput(text="RCLLA"), {"a": 5, "b": 8})
    assert res.output_text == "HELLO"
    
def test_playfair() -> None:
    decoder = PlayfairDecoder()
    res = decoder.run(DecoderInput(text="HELLO"), {"mode": "encrypt", "key": "PLAYFAIR", "replace": "J=I"})
    cipher = res.output_text
    res_dec = decoder.run(DecoderInput(text=cipher), {"mode": "decrypt", "key": "PLAYFAIR", "replace": "J=I"})
    assert "HELXLO" in res_dec.output_text

def test_hill() -> None:
    decoder = HillDecoder()
    res = decoder.run(DecoderInput(text="HELP"), {"mode": "encrypt", "matrix": "3,3,2,5"})
    assert res.success
    cipher = res.output_text
    res_dec = decoder.run(DecoderInput(text=cipher), {"mode": "decrypt", "matrix": "3,3,2,5"})
    assert res_dec.output_text == "HELP"

def test_flag_awareness() -> None:
    decoder = CaesarDecoder()
    res = decoder.run(DecoderInput(text="CTK{KHOOR}"), {"shift": 3})
    assert res.success
    assert res.output_text == "CTK{HELLO}"
    assert "Potential Flag" in res.warnings
