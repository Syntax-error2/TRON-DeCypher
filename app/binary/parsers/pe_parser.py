from app.binary.analyzers.api_classification import api_classification_service
from app.binary.models import BinaryAnalysisResult, BinarySection, ImportExport

try:
    import pefile
    HAS_PEFILE = True
except ImportError:
    HAS_PEFILE = False

class PEParser:
    """Safely parses PE binaries statically using pefile."""
    
    def parse(self, filepath: str, result: BinaryAnalysisResult) -> None:
        if not HAS_PEFILE:
            result.findings.append("ERROR: 'pefile' module not installed. Detailed PE parsing unavailable.")
            return
            
        try:
            # We use fast_load to avoid recursively parsing the whole file immediately
            pe = pefile.PE(filepath, fast_load=True)
            
            result.architecture = "x64" if pe.FILE_HEADER.Machine == 0x8664 else "x86"
            result.bitness = "64-bit" if result.architecture == "x64" else "32-bit"
            result.endianness = "little-endian"
            
            # Use safe getattr for Optional fields
            opt_header = getattr(pe, "OPTIONAL_HEADER", None)
            if opt_header:
                result.entry_point = opt_header.ImageBase + opt_header.AddressOfEntryPoint
                
                # Protections
                dll_char = opt_header.DllCharacteristics
                if dll_char:
                    result.protections.nx = "Enabled" if (dll_char & 0x0100) else "Disabled" # IMAGE_DLLCHARACTERISTICS_NX_COMPAT
                    result.protections.pie = "Enabled" if (dll_char & 0x0040) else "Disabled" # IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE
                    result.protections.aslr = result.protections.pie
                    
            # Parse sections
            for section in pe.sections:
                sec_name = section.Name.decode('utf-8', errors='ignore').strip('\x00')
                chars = section.Characteristics
                perms = ""
                if chars & 0x40000000: perms += "R"
                if chars & 0x80000000: perms += "W"
                if chars & 0x20000000: perms += "X"
                
                bs = BinarySection(
                    name=sec_name,
                    virtual_address=section.VirtualAddress,
                    virtual_size=section.Misc_VirtualSize,
                    raw_size=section.SizeOfRawData,
                    offset=section.PointerToRawData,
                    entropy=section.get_entropy(),
                    permissions=perms
                )
                result.sections.append(bs)
                
            # Parse imports/exports (must do full load now for directories)
            pe.parse_data_directories()
            
            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    lib_name = entry.dll.decode('utf-8', errors='ignore') if entry.dll else "Unknown"
                    for imp in entry.imports:
                        func_name = imp.name.decode('utf-8', errors='ignore') if imp.name else f"Ordinal_{imp.ordinal}"
                        cat = api_classification_service.classify(func_name)
                        result.imports.append(ImportExport(
                            is_import=True,
                            library=lib_name,
                            function=func_name,
                            address=imp.address,
                            category=cat
                        ))
                        
            if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
                for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                    func_name = exp.name.decode('utf-8', errors='ignore') if exp.name else f"Ordinal_{exp.ordinal}"
                    result.exports.append(ImportExport(
                        is_import=False,
                        library="Self",
                        function=func_name,
                        address=pe.OPTIONAL_HEADER.ImageBase + exp.address if opt_header else exp.address,
                        ordinal=exp.ordinal
                    ))
                    
        except Exception as e:
            result.findings.append(f"ERROR: Failed to parse PE: {e}")

pe_parser = PEParser()
