from app.binary.models import BinaryAnalysisResult


class ObfuscationAnalyzer:
    """Statically hints at possible packing or obfuscation based on heuristics."""
    
    def analyze(self, result: BinaryAnalysisResult) -> None:
        hints = []
        
        # 1. Few imports
        if len(result.imports) > 0 and len(result.imports) < 5:
            hints.append("Very few imports discovered. (Potential packer/dropper)")
            
        # 2. Suspicious section names
        suspicious_sections = [".upx", ".aspack", ".vmp", ".themida"]
        for sec in result.sections:
            if any(s in sec.name.lower() for s in suspicious_sections):
                hints.append(f"Suspicious section name '{sec.name}' discovered.")
                
            # 3. High entropy section
            if sec.entropy > 7.2:
                hints.append(f"Section '{sec.name}' has very high entropy ({sec.entropy:.2f}).")
                
            # 4. Writable & Executable
            if "W" in sec.permissions and "X" in sec.permissions:
                hints.append(f"Section '{sec.name}' is Writable and Executable (RWX).")
                
        # 5. Zero-size virtual sections with large raw data, or vice versa
        for sec in result.sections:
            if sec.virtual_size > 0 and sec.raw_size == 0:
                # BSS is normal, but very large can be unpacking space
                if sec.virtual_size > 1000000:
                    hints.append(f"Section '{sec.name}' allocates large virtual space with no raw data (Unpacking area?).")
                    
        if len(hints) >= 2:
            result.is_packed_hint = True
            
        for h in set(hints):
            result.findings.append(f"LOW: {h}")

obfuscation_analyzer = ObfuscationAnalyzer()
