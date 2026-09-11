import zlib
from typing import Any

from app.decoders.core.base import DecoderBase
from app.decoders.core.models import DecoderInput, DecoderResult


class GzipDecoder(DecoderBase):
    name = "Gzip"
    category = "compression"
    reversible = True
    input_types = ["bytes"]
    output_types = ["bytes"]
    description = "Compress or decompress using Gzip."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decompress") # "compress" or "decompress"
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        try:
            if mode == "decompress":
                out = zlib.decompress(data, 15 + 32)
            else:
                out = zlib.compress(data)
            return self._create_result(True, output_data=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.data and input_data.data.startswith(b'\x1f\x8b'):
            return 1.0, {"reason": "Gzip magic bytes"}
        return 0.0, {}

class ZlibDecoder(DecoderBase):
    name = "Zlib"
    category = "compression"
    reversible = True
    input_types = ["bytes"]
    output_types = ["bytes"]
    description = "Compress or decompress using Zlib."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decompress")
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        try:
            if mode == "decompress":
                out = zlib.decompress(data)
            else:
                out = zlib.compress(data)
            return self._create_result(True, output_data=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        if input_data.data and input_data.data.startswith(b'\x78'):
            return 0.7, {"reason": "Zlib magic byte candidate"}
        return 0.0, {}

class DeflateDecoder(DecoderBase):
    name = "Deflate"
    category = "compression"
    reversible = True
    input_types = ["bytes"]
    output_types = ["bytes"]
    description = "Compress or decompress using raw Deflate."
    
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        mode = context.get("mode", "decompress")
        data = input_data.data if input_data.data else (input_data.text.encode('utf-8') if input_data.text else b"")
        try:
            if mode == "decompress":
                out = zlib.decompress(data, -15)
            else:
                comp = zlib.compressobj(9, zlib.DEFLATED, -15)
                out = comp.compress(data) + comp.flush()
            return self._create_result(True, output_data=out)
        except Exception as e:
            return self._create_result(False, errors=[str(e)])
            
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        return 0.0, {}
