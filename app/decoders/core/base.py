import re
import time
from abc import abstractmethod
from typing import Any

from app.decoders.core.models import DecoderInput, DecoderResult
from app.plugins.base import PluginBase


class DecoderBase(PluginBase):
    '''Base class for all decoders.'''
    
    category: str = "general"
    reversible: bool = True
    input_types: list[str] = ["text"]
    output_types: list[str] = ["text"]
    expected_params: dict[str, dict[str, Any]] = {}
    
    FLAG_PATTERN = re.compile(r'^(CTK|FLAG|TRON|CTF|HTB|THM)\{(.*?)\}$', re.IGNORECASE)
    
    def _extract_flag(self, text: str) -> tuple[str, str, str]:
        '''Returns (prefix, inner, suffix) if flag found, else ("", text, "").'''
        m = self.FLAG_PATTERN.match(text.strip())
        if m:
            prefix = m.group(1) + "{"
            inner = m.group(2)
            suffix = "}"
            return prefix, inner, suffix
        return "", text, ""

    @abstractmethod
    def decode(self, input_data: DecoderInput, context: dict[str, Any]) -> DecoderResult:
        '''Perform the decoding transformation.'''
        
    @abstractmethod
    def detect(self, input_data: DecoderInput) -> tuple[float, dict[str, Any]]:
        '''Analyze input and return a tuple of (confidence, reasons/metadata).'''
        
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, DecoderInput)
        
    def run(self, input_data: Any, context: dict[str, Any]) -> Any:
        '''Alias for decode to satisfy PluginBase interface.'''
        if not isinstance(input_data, DecoderInput):
            if isinstance(input_data, str):
                input_data = DecoderInput(text=input_data)
            elif isinstance(input_data, bytes):
                input_data = DecoderInput(data=input_data, source_type="bytes")
            else:
                raise ValueError("DecoderInput expected")
                
        # Flag-Aware wrapping (for text only)
        prefix, inner_text, suffix = "", "", ""
        if input_data.text:
            prefix, inner_text, suffix = self._extract_flag(input_data.text)
            if prefix:
                input_data = DecoderInput(text=inner_text, data=input_data.data, source_type=input_data.source_type, encoding=input_data.encoding)
                
        result = self.decode(input_data, context)
        
        # Restore flag wrapper if successful text output
        if prefix and result.success and result.output_text:
            result.output_text = f"{prefix}{result.output_text}{suffix}"
            if "Potential Flag" not in result.warnings:
                result.warnings.append("Potential Flag")
                
        return result
        
    def _create_result(self, success: bool, output_text: str | None = None, output_data: bytes | None = None, 
                       confidence: float = 0.0, errors: list[str] | None = None, 
                       warnings: list[str] | None = None, metadata: dict[str, Any] | None = None, 
                       start_time: float = 0.0) -> DecoderResult:
        return DecoderResult(
            success=success,
            decoder=self.name,
            output_text=output_text,
            output_data=output_data,
            output_type="bytes" if output_data is not None else "text",
            confidence=confidence,
            errors=errors or [],
            warnings=warnings or [],
            metadata=metadata or {},
            execution_time=time.time() - start_time if start_time else 0.0
        )
