
from app.decoders.classical.caesar import CaesarDecoder
from app.decoders.classical.vigenere import VigenereDecoder
from app.decoders.classical.affine import AffineDecoder
from app.decoders.classical.autokey import AutokeyDecoder
from app.decoders.classical.playfair import PlayfairDecoder
from app.decoders.classical.hill import HillDecoder
from app.decoders.classical.polybius_based import PolybiusDecoder, TapCodeDecoder, A1Z26Decoder
from app.decoders.classical.fractional import BifidDecoder, TrifidDecoder
from app.decoders.classical.transposition import ColumnarTranspositionDecoder, RailFenceDecoder, ScytaleDecoder
from app.decoders.classical.keyboard_shift import KeyboardShiftDecoder
from app.decoders.binary.xor_decoder import XorDecoder
from app.decoders.classical.atbash_decoder import AtbashDecoder
from app.decoders.classical.morse_decoder import MorseDecoder
from app.decoders.classical.rot_decoder import RotDecoder
from app.decoders.core.detector import decoder_detector
from app.decoders.core.pipeline import PipelineRunner
from app.decoders.core.registry import decoder_registry
from app.decoders.encoding.base32_decoder import Base32Decoder
from app.decoders.encoding.base64_decoder import Base64Decoder
from app.decoders.encoding.base_ex_decoder import Base58Decoder, Base85Decoder
from app.decoders.encoding.compression import DeflateDecoder, GzipDecoder, ZlibDecoder
from app.decoders.encoding.hash_generator import HashGenerator
from app.decoders.encoding.hex_decoder import HexDecoder
from app.decoders.encoding.jwt_decoder import JwtDecoder
from app.decoders.numeric.binary_decoder import BinaryAsciiDecoder
from app.decoders.numeric.numeric_ex_decoder import (
    BitwiseNotDecoder,
    ByteSwapDecoder,
    DecimalAsciiDecoder,
    OctalAsciiDecoder,
)
from app.decoders.text.html_decoder import HtmlDecoder
from app.decoders.text.text_ex_decoder import JsonEscapeDecoder, PunycodeDecoder
from app.decoders.text.text_transforms import (
    BaconDecoder,
    BeaufortDecoder,
    ReverseDecoder,
    WhitespaceNormalizationDecoder,
)
from app.decoders.text.unicode_decoder import UnicodeEscapeDecoder
from app.decoders.text.url_decoder import UrlDecoder


def register_all_decoders() -> None:

    decoder_registry.register(CaesarDecoder())
    decoder_registry.register(VigenereDecoder())
    decoder_registry.register(AffineDecoder())
    decoder_registry.register(AutokeyDecoder())
    decoder_registry.register(PlayfairDecoder())
    decoder_registry.register(HillDecoder())
    decoder_registry.register(PolybiusDecoder())
    decoder_registry.register(TapCodeDecoder())
    decoder_registry.register(A1Z26Decoder())
    decoder_registry.register(BifidDecoder())
    decoder_registry.register(TrifidDecoder())
    decoder_registry.register(ColumnarTranspositionDecoder())
    decoder_registry.register(RailFenceDecoder())
    decoder_registry.register(ScytaleDecoder())
    decoder_registry.register(KeyboardShiftDecoder())
    decoder_registry.register(Base58Decoder())
    decoder_registry.register(Base85Decoder())
    decoder_registry.register(GzipDecoder())
    decoder_registry.register(ZlibDecoder())
    decoder_registry.register(DeflateDecoder())
    decoder_registry.register(HashGenerator())
    decoder_registry.register(JwtDecoder())
    decoder_registry.register(DecimalAsciiDecoder())
    decoder_registry.register(OctalAsciiDecoder())
    decoder_registry.register(BitwiseNotDecoder())
    decoder_registry.register(ByteSwapDecoder())
    decoder_registry.register(PunycodeDecoder())
    decoder_registry.register(JsonEscapeDecoder())
    decoder_registry.register(ReverseDecoder())
    decoder_registry.register(WhitespaceNormalizationDecoder())
    decoder_registry.register(BaconDecoder())
    decoder_registry.register(BeaufortDecoder())
    decoder_registry.register(Base64Decoder())
    decoder_registry.register(Base32Decoder())
    decoder_registry.register(HexDecoder())
    decoder_registry.register(UrlDecoder())
    decoder_registry.register(HtmlDecoder())
    decoder_registry.register(UnicodeEscapeDecoder())
    decoder_registry.register(RotDecoder())
    decoder_registry.register(MorseDecoder())
    decoder_registry.register(AtbashDecoder())
    decoder_registry.register(XorDecoder())
    decoder_registry.register(BinaryAsciiDecoder())

__all__ = [
    "PipelineRunner",
    "decoder_detector",
    "decoder_registry",
    "register_all_decoders"
]

