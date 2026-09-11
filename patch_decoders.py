from app.decoders.classical.caesar import CaesarDecoder
from app.decoders.classical.vigenere import VigenereDecoder
from app.decoders.classical.affine import AffineDecoder
from app.decoders.classical.autokey import AutokeyDecoder
from app.decoders.classical.playfair import PlayfairDecoder
from app.decoders.classical.hill import HillDecoder
from app.decoders.classical.polybius_based import PolybiusDecoder, TapCodeDecoder
from app.decoders.classical.fractional import BifidDecoder, TrifidDecoder
from app.decoders.classical.transposition import ColumnarTranspositionDecoder, RailFenceDecoder, ScytaleDecoder
from app.decoders.classical.keyboard_shift import KeyboardShiftDecoder

def add_new_decoders(registry):
    registry.register(CaesarDecoder())
    registry.register(VigenereDecoder())
    registry.register(AffineDecoder())
    registry.register(AutokeyDecoder())
    registry.register(PlayfairDecoder())
    registry.register(HillDecoder())
    registry.register(PolybiusDecoder())
    registry.register(TapCodeDecoder())
    registry.register(BifidDecoder())
    registry.register(TrifidDecoder())
    registry.register(ColumnarTranspositionDecoder())
    registry.register(RailFenceDecoder())
    registry.register(ScytaleDecoder())
    registry.register(KeyboardShiftDecoder())
