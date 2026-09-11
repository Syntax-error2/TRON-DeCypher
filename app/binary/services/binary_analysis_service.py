import math
import os

from app.analyzers.core.string_extractor import StringExtractorAnalyzer
from app.binary.analyzers.obfuscation import obfuscation_analyzer
from app.binary.models import BinaryAnalysisResult
from app.binary.parsers.elf_parser import elf_parser
from app.binary.parsers.identification import binary_identification_analyzer
from app.binary.parsers.pe_parser import pe_parser
from app.osint.extraction import ioc_extraction_service


class BinaryAnalysisService:
    """Orchestrates static binary analysis parsing."""
    
    def analyze(self, filepath: str) -> BinaryAnalysisResult:
        result = BinaryAnalysisResult(file_path=filepath)
        
        if not os.path.exists(filepath):
            result.findings.append(f"ERROR: File {filepath} not found.")
            return result
            
        with open(filepath, 'rb') as f:
            header = f.read(4096)
            
        result.format = binary_identification_analyzer.identify(header)
        
        if result.format == "PE":
            pe_parser.parse(filepath, result)
        elif result.format == "ELF":
            elf_parser.parse(filepath, result)
        elif result.format == "Mach-O":
            result.findings.append("Mach-O parsed identified, but deep parsing is not yet implemented.")
        else:
            result.findings.append("Unknown format. Binary parsers skipped.")
            
        # Re-use Phase 2 entropy logic for the overall file
        with open(filepath, 'rb') as f:
            data = f.read()
            result.entropy = self._calculate_entropy(data)
            
        # Re-use Phase 2 string extraction
        try:
            extractor = StringExtractorAnalyzer()
            strings_list = extractor.run(filepath, {})
            if strings_list:
                for s in strings_list:
                    result.strings.append({
                        "string": s.string,
                        "encoding": s.encoding,
                        "offset": s.offset
                    })
        except Exception as e:
            result.findings.append(f"String extraction failed: {e}")
            
        # Extract IOCs from strings
        combined_strings = "\n".join([s["string"] for s in result.strings])
        iocs = ioc_extraction_service.extract(combined_strings, case_id="binary_analysis")
        if iocs:
            result.findings.append(f"Extracted {len(iocs)} IOCs from binary strings.")
            
        # Obfuscation hints
        obfuscation_analyzer.analyze(result)
        
        return result
        
    def _calculate_entropy(self, data: bytes) -> float:
        if not data: return 0.0
        entropy = 0.0
        length = len(data)
        counts = [0] * 256
        for b in data: counts[b] += 1
        for count in counts:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return entropy

binary_analysis_service = BinaryAnalysisService()
