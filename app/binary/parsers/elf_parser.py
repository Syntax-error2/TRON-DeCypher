import math
from typing import Any

from app.binary.analyzers.api_classification import api_classification_service
from app.binary.models import BinaryAnalysisResult, BinarySection, ImportExport

try:
    from elftools.elf.dynamic import DynamicSection
    from elftools.elf.elffile import ELFFile
    from elftools.elf.sections import SymbolTableSection
    HAS_ELFTOOLS = True
except ImportError:
    HAS_ELFTOOLS = False

class ELFParser:
    """Safely parses ELF binaries statically using pyelftools."""
    
    def parse(self, filepath: str, result: BinaryAnalysisResult) -> None:
        if not HAS_ELFTOOLS:
            result.findings.append("ERROR: 'pyelftools' module not installed. Detailed ELF parsing unavailable.")
            return
            
        try:
            with open(filepath, 'rb') as f:
                elf = ELFFile(f)
                
                result.architecture = elf.get_machine_arch()
                result.bitness = "64-bit" if elf.elfclass == 64 else "32-bit"
                result.endianness = "little-endian" if elf.little_endian else "big-endian"
                result.entry_point = elf.header['e_entry']
                
                # Sections
                for section in elf.iter_sections():
                    flags = section['sh_flags']
                    perms = ""
                    # 1 = SHF_WRITE, 2 = SHF_ALLOC, 4 = SHF_EXECINSTR
                    if flags & 2: perms += "R"
                    if flags & 1: perms += "W"
                    if flags & 4: perms += "X"
                    
                    data = section.data()
                    entropy = self._calculate_entropy(data) if data else 0.0
                    
                    bs = BinarySection(
                        name=section.name,
                        virtual_address=section['sh_addr'],
                        virtual_size=section['sh_size'],
                        raw_size=len(data),
                        offset=section['sh_offset'],
                        entropy=entropy,
                        permissions=perms
                    )
                    result.sections.append(bs)
                    
                # Dynamic Tags / Relocations (Imports/Exports approx)
                for section in elf.iter_sections():
                    if isinstance(section, DynamicSection):
                        for tag in section.iter_tags():
                            if tag.entry.d_tag == 'DT_NEEDED':
                                result.imports.append(ImportExport(
                                    is_import=True,
                                    library=getattr(tag, "needed", "Unknown"),
                                    function="<library_load>",
                                    category="Library"
                                ))
                                
                    if isinstance(section, SymbolTableSection):
                        for symbol in section.iter_symbols():
                            if not symbol.name: continue
                            
                            # Extremely simplified import/export logic for ELF
                            info_bind = symbol['st_info']['bind']
                            info_type = symbol['st_info']['type']
                            
                            if info_type == 'STT_FUNC':
                                if symbol['st_shndx'] == 'SHN_UNDEF':
                                    # Undefined function = Import
                                    cat = api_classification_service.classify(symbol.name)
                                    result.imports.append(ImportExport(
                                        is_import=True,
                                        library="Unknown",
                                        function=symbol.name,
                                        address=symbol['st_value'],
                                        category=cat
                                    ))
                                elif info_bind in ('STB_GLOBAL', 'STB_WEAK'):
                                    # Export / Defined global function
                                    result.exports.append(ImportExport(
                                        is_import=False,
                                        library="Self",
                                        function=symbol.name,
                                        address=symbol['st_value']
                                    ))
                                    
                # Protections
                result.protections.nx = "Enabled" if self._has_nx(elf) else "Disabled"
                result.protections.pie = "Enabled" if elf.header['e_type'] == 'ET_DYN' else "Disabled"
                
        except Exception as e:
            result.findings.append(f"ERROR: Failed to parse ELF: {e}")
            
    def _has_nx(self, elf: Any) -> bool:
        for segment in elf.iter_segments():
            if segment['p_type'] == 'PT_GNU_STACK':
                return not (segment['p_flags'] & 1) # PF_X is 1
        return False
        
    def _calculate_entropy(self, data: bytes) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        counts = [0] * 256
        for b in data:
            counts[b] += 1
        for count in counts:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return entropy

elf_parser = ELFParser()
