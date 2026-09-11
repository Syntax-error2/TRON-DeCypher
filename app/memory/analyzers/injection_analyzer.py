from app.memory.models import MemoryAnalysisResult, MemoryFinding


class InjectionAnalyzer:
    """Conservatively looks for injection indicators from the parsed output."""
    
    def analyze(self, result: MemoryAnalysisResult) -> None:
        # 1. Suspicious Process Names
        suspicious_names = ["svchost.exe", "lsass.exe", "csrss.exe", "winlogon.exe", "explorer.exe"]
        for p in result.processes:
            if p.name.lower() in suspicious_names:
                # Look for misspellings like svch0st.exe? 
                pass
            if "svch" in p.name.lower() and p.name.lower() != "svchost.exe":
                result.findings.append(MemoryFinding(
                    severity="HIGH",
                    description=f"Suspiciously named process: {p.name} (PID: {p.pid})",
                    source="Injection Analyzer"
                ))
                
        # 2. Modules without backing files
        for m in result.modules:
            if not m.path or "unknown" in m.path.lower() or m.path.isspace():
                result.findings.append(MemoryFinding(
                    severity="MEDIUM",
                    description=f"Module '{m.name}' in PID {m.pid} has no backing path (Possible injection/hollowing).",
                    source="Injection Analyzer"
                ))
                
        # 3. Suspicious temporary directories
        for m in result.modules:
            if m.path and ("\\temp\\" in m.path.lower() or "\\appdata\\local\\temp\\" in m.path.lower()):
                result.findings.append(MemoryFinding(
                    severity="LOW",
                    description=f"Module loaded from temporary path: {m.path}",
                    source="Injection Analyzer"
                ))

injection_analyzer = InjectionAnalyzer()
