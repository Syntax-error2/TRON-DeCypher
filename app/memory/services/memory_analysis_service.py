import logging

from app.analyzers.core.string_extractor import StringExtractorAnalyzer
from app.memory.analyzers.injection_analyzer import injection_analyzer
from app.memory.analyzers.memory_identification import memory_identification_analyzer
from app.memory.integrations.volatility_integration import volatility_integration_service
from app.memory.models import MemoryAnalysisResult, MemoryFinding
from app.memory.parsers.volatility_parser import volatility_parser
from app.osint.extraction import ioc_extraction_service

logger = logging.getLogger(__name__)

class MemoryAnalysisService:
    """Orchestrates memory forensics."""
    
    def analyze(self, filepath: str) -> MemoryAnalysisResult:
        result = MemoryAnalysisResult(file_path=filepath)
        
        # 1. Identification
        memory_identification_analyzer.analyze(filepath, result)
        
        # 2. String Extraction
        try:
            extractor = StringExtractorAnalyzer()
            strings_list = extractor.run(filepath, {"min_length": 6, "max_count": 2000})
            if strings_list:
                for s in strings_list:
                    result.strings.append({
                        "string": s.string,
                        "encoding": s.encoding,
                        "offset": s.offset
                    })
        except Exception as e:
            result.findings.append(MemoryFinding("LOW", f"String extraction failed: {e}", "Service"))
            
        # 3. IOC Extraction
        combined_strings = "\n".join([s["string"] for s in result.strings])
        iocs = ioc_extraction_service.extract(combined_strings, case_id="memory_analysis")
        if iocs:
            result.iocs_extracted = len(iocs)
            result.findings.append(MemoryFinding("INFO", f"Extracted {len(iocs)} IOCs from memory strings.", "IOC Service"))
            
        # 4. Volatility Execution
        if volatility_integration_service.is_available():
            logger.info("Volatility is available. Executing plugins...")
            
            # windows.pslist
            pslist_data = volatility_integration_service.run_plugin(filepath, "windows.pslist.PsList")
            if pslist_data:
                volatility_parser.parse_pslist(pslist_data, result)
            else:
                result.findings.append(MemoryFinding("LOW", "windows.pslist returned no data or failed.", "Volatility"))
                
            # windows.netscan
            netscan_data = volatility_integration_service.run_plugin(filepath, "windows.netscan.NetScan")
            if netscan_data:
                volatility_parser.parse_netscan(netscan_data, result)
                
            # windows.dlllist
            dlllist_data = volatility_integration_service.run_plugin(filepath, "windows.dlllist.DllList")
            if dlllist_data:
                volatility_parser.parse_dlllist(dlllist_data, result)
                
        else:
            result.findings.append(MemoryFinding("INFO", "Volatility 3 not found. Deep process analysis skipped.", "Integration"))
            
        # Correlate modules to processes
        proc_dict = {p.pid: p.name for p in result.processes}
        for m in result.modules:
            if m.pid in proc_dict:
                m.process_name = proc_dict[m.pid]
                
        # 5. Anomaly analysis
        injection_analyzer.analyze(result)
        
        return result

memory_analysis_service = MemoryAnalysisService()
