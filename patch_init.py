with open('app/decoders/__init__.py', 'r', encoding='utf-8') as f:
    content = f.read()

imports = '''
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
'''

registrations = '''
    decoder_registry.register(CaesarDecoder())
    decoder_registry.register(VigenereDecoder())
    decoder_registry.register(AffineDecoder())
    decoder_registry.register(AutokeyDecoder())
    decoder_registry.register(PlayfairDecoder())
    decoder_registry.register(HillDecoder())
    decoder_registry.register(PolybiusDecoder())
    decoder_registry.register(TapCodeDecoder())
    decoder_registry.register(BifidDecoder())
    decoder_registry.register(TrifidDecoder())
    decoder_registry.register(ColumnarTranspositionDecoder())
    decoder_registry.register(RailFenceDecoder())
    decoder_registry.register(ScytaleDecoder())
    decoder_registry.register(KeyboardShiftDecoder())
'''

# insert imports at top
content = imports + content

# insert registrations in register_all_decoders
content = content.replace('    decoder_registry.register(Base58Decoder())', registrations + '    decoder_registry.register(Base58Decoder())')

with open('app/decoders/__init__.py', 'w', encoding='utf-8') as f:
    f.write(content)
