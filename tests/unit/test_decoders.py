from app.decoders.binary.xor_decoder import XorDecoder
from app.decoders.classical.rot_decoder import RotDecoder
from app.decoders.core.detector import DecoderDetectionService
from app.decoders.core.models import DecoderInput, TransformationPipeline, TransformationStep
from app.decoders.core.pipeline import PipelineRunner
from app.decoders.core.registry import DecoderRegistry
from app.decoders.encoding.base64_decoder import Base64Decoder
from app.decoders.encoding.hex_decoder import HexDecoder


def test_base64_decoder() -> None:
    decoder = Base64Decoder()
    inp = DecoderInput(text="SGVsbG8=")
    result = decoder.decode(inp, {})
    assert result.success
    assert result.output_text == "Hello"

def test_hex_decoder() -> None:
    decoder = HexDecoder()
    inp = DecoderInput(text="48656c6c6f")
    result = decoder.decode(inp, {})
    assert result.success
    assert result.output_text == "Hello"
    
def test_hex_decoder_with_spaces() -> None:
    decoder = HexDecoder()
    inp = DecoderInput(text="48 65 6c 6c 6f")
    result = decoder.decode(inp, {})
    assert result.success
    assert result.output_text == "Hello"

def test_rot_decoder() -> None:
    decoder = RotDecoder()
    inp = DecoderInput(text="Uryyb")
    result = decoder.decode(inp, {"variant": "rot13"})
    assert result.success
    assert result.output_text == "Hello"

def test_xor_decoder() -> None:
    decoder = XorDecoder()
    # "Hello" ^ 0x42
    inp = DecoderInput(data=b'\x0a\x27\x2e\x2e\x2d')
    result = decoder.decode(inp, {"key": 0x42})
    assert result.success
    assert result.output_text == "Hello"

def test_pipeline_runner() -> None:
    registry = DecoderRegistry()
    registry.register(HexDecoder())
    registry.register(Base64Decoder())
    
    runner = PipelineRunner(registry)
    
    pipeline = TransformationPipeline(id="test_pl")
    pipeline.steps.append(TransformationStep(id="s1", decoder_name="hex"))
    pipeline.steps.append(TransformationStep(id="s2", decoder_name="base64"))
    
    # Input is Hex encoded Base64 encoded "Hello"
    # "Hello" -> "SGVsbG8=" -> "534756736247383D"
    inp = DecoderInput(text="534756736247383D")
    results = runner.run_pipeline(pipeline, inp)
    
    assert len(results) == 2
    assert results[0].success
    assert results[0].output_text == "SGVsbG8="
    assert results[1].success
    assert results[1].output_text == "Hello"

def test_detection() -> None:
    registry = DecoderRegistry()
    registry.register(Base64Decoder())
    registry.register(HexDecoder())
    
    detector = DecoderDetectionService(registry)
    
    # "Hello" in Base64
    inp = DecoderInput(text="SGVsbG8=")
    results = detector.detect(inp)
    
    assert len(results) > 0
    assert results[0].decoder_name == "base64"
    assert results[0].confidence > 0.8
