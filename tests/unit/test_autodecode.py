from app.decoders.core.autodecode import AutoDecodeService
from app.decoders.core.detector import DecoderDetectionService
from app.decoders.core.models import DecoderInput
from app.decoders.core.pipeline import PipelineRunner
from app.decoders.core.registry import DecoderRegistry
from app.decoders.encoding.base64_decoder import Base64Decoder
from app.decoders.encoding.hex_decoder import HexDecoder


def test_auto_decode() -> None:
    registry = DecoderRegistry()
    registry.register(HexDecoder())
    registry.register(Base64Decoder())
    
    runner = PipelineRunner(registry)
    detector = DecoderDetectionService(registry)
    auto = AutoDecodeService(runner, detector)
    
    # "Hello" -> Base64: "SGVsbG8=" -> Hex: "534756736247383D"
    inp = DecoderInput(text="534756736247383D")
    pipeline = auto.auto_decode(inp)
    
    assert len(pipeline.steps) == 2
    assert pipeline.steps[0].decoder_name == "hex"
    assert pipeline.steps[1].decoder_name == "base64"
    
    # Result of second step should be "Hello"
    assert pipeline.steps[1].result is not None
    assert pipeline.steps[1].result.output_text == "Hello"
