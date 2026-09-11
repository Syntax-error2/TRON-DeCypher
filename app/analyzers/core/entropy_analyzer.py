import logging
import math
from pathlib import Path
from typing import Any

from app.models.triage import EntropyResult
from app.plugins.base import PluginBase

logger = logging.getLogger(__name__)

class EntropyAnalyzer(PluginBase):
    name = "entropy_analyzer"
    version = "1.0.0"
    category = "core"
    description = "Calculates Shannon entropy."
    supported_input_types = ["file"]
    
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, (str, Path)) and Path(input_data).is_file()
        
    def _calculate_shannon(self, data: bytes) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        counts = [0] * 256
        for byte in data:
            counts[byte] += 1
            
        for count in counts:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return entropy

    def run(self, input_data: Any, context: dict[str, Any]) -> EntropyResult:
        path = Path(input_data)
        window_size = context.get("window_size", 4096)
        
        # Calculate full file entropy without reading entirely into memory if possible, 
        # but for Shannon we need counts. We can stream to get counts!
        counts = [0] * 256
        length = 0
        
        max_entropy = 0.0
        max_entropy_offset = 0
        
        offset = 0
        with open(path, "rb") as f:
            while chunk := f.read(window_size):
                chunk_len = len(chunk)
                length += chunk_len
                
                # Update global counts
                for byte in chunk:
                    counts[byte] += 1
                    
                # Calculate window entropy
                window_entropy = self._calculate_shannon(chunk)
                if window_entropy > max_entropy:
                    max_entropy = window_entropy
                    max_entropy_offset = offset
                    
                offset += chunk_len
                
        # Final global entropy
        global_entropy = 0.0
        if length > 0:
            for count in counts:
                if count > 0:
                    p = count / length
                    global_entropy -= p * math.log2(p)
                    
        # By default, we might return the global entropy, but we can include window info
        return EntropyResult(
            entropy=global_entropy,
            window=window_size if length > window_size else None,
            offset=max_entropy_offset if length > window_size else None
        )
