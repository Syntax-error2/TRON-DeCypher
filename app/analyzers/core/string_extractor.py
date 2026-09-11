import logging
import string
from pathlib import Path
from typing import Any

from app.models.triage import StringResult
from app.plugins.base import PluginBase

logger = logging.getLogger(__name__)

class StringExtractorAnalyzer(PluginBase):
    name = "string_extractor"
    version = "1.0.0"
    category = "core"
    description = "Extracts printable strings from binary data."
    supported_input_types = ["file"]
    
    # Standard printable ascii
    PRINTABLE = set(string.printable.encode('ascii'))
    
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, (str, Path)) and Path(input_data).is_file()
        
    def run(self, input_data: Any, context: dict[str, Any]) -> list[StringResult]:
        path = Path(input_data)
        min_length = context.get("min_length", 4)
        max_count = context.get("max_count", 1000)
        
        results: list[StringResult] = []
        
        # Simple ascii extraction (very basic implementation for Phase 2)
        # Note: robust utf-16 extraction is more complex, but we'll do a basic sweep.
        with open(path, "rb") as f:
            chunk_size = 4096
            offset = 0
            current_string = bytearray()
            current_offset = 0
            
            while chunk := f.read(chunk_size):
                for i, byte in enumerate(chunk):
                    if byte in self.PRINTABLE:
                        if not current_string:
                            current_offset = offset + i
                        current_string.append(byte)
                    else:
                        if len(current_string) >= min_length:
                            try:
                                decoded = current_string.decode('ascii')
                                results.append(StringResult(
                                    offset=current_offset,
                                    encoding="ascii",
                                    string=decoded
                                ))
                                if len(results) >= max_count:
                                    return results
                            except UnicodeDecodeError:
                                pass
                        current_string = bytearray()
                offset += len(chunk)
                
            # catch trailing
            if len(current_string) >= min_length:
                try:
                    results.append(StringResult(
                        offset=current_offset,
                        encoding="ascii",
                        string=current_string.decode('ascii')
                    ))
                except UnicodeDecodeError:
                    pass
                    
        return results[:max_count]
