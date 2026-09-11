class BinaryIdentificationAnalyzer:
    """Uses magic bytes to safely identify binary types before deep parsing."""
    
    def identify(self, data: bytes) -> str:
        if len(data) < 4:
            return "Unknown"
            
        magic = data[:4]
        
        # ELF: 7F 45 4C 46 (\x7fELF)
        if magic == b'\x7fELF':
            return "ELF"
            
        # PE: 4D 5A (MZ)
        if magic[:2] == b'MZ':
            # Could be DOS or PE, deep parse will confirm PE header
            return "PE"
            
        # Mach-O: FE ED FA CE, CE FA ED FE, FE ED FA CF, CF FA ED FE, CA FE BA BE
        if magic in (b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', 
                     b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', 
                     b'\xca\xfe\xba\xbe'):
            return "Mach-O"
            
        return "Unknown"

binary_identification_analyzer = BinaryIdentificationAnalyzer()
