import importlib.metadata
import importlib.util
import logging
import os
import shutil
import subprocess

from app.models.tool import Tool

logger = logging.getLogger(__name__)

class ToolService:
    def __init__(self) -> None:
        self.tools: dict[str, Tool] = {}
        
    def scan_for_tools(self) -> None:
        logger.info("Scanning for capabilities, python packages, and external tools...")
        self.tools.clear()
        
        self._scan_builtin()
        self._scan_python_packages()
        self._scan_executables()
        
    def _add_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool
        
    def _scan_builtin(self) -> None:
        builtins = [
            ("File Hashing", ["MD5", "SHA1", "SHA256", "SSDEEP"]),
            ("File Identification", ["Magic", "Signatures"]),
            ("String Extraction", ["ASCII", "UTF16"]),
            ("Entropy Analysis", ["Shannon", "Blocks"]),
            ("Decoder", ["Base64", "Hex", "ROT", "URL"]),
            ("IOC Extraction", ["IP", "Domain", "Hash"]),
            ("Quick Triage", ["Ingest", "Queue"]),
            ("PE Parser", ["Headers", "Sections", "Imports"]),
            ("ELF Parser", ["Headers", "Sections"]),
            ("HTTP Parser", ["Headers", "Body", "JWT"]),
            ("PCAP File Analysis", ["scapy.utils.PcapReader"])
        ]
        
        for name, caps in builtins:
            t = Tool(
                id=f"builtin_{name.lower().replace(' ', '_')}",
                name=name,
                executable="",
                tool_type="BUILT-IN",
                status="AVAILABLE",
                detection_method="TRON-DeCypher Core",
                capabilities=caps
            )
            self._add_tool(t)
            
    def _scan_python_packages(self) -> None:
        packages = [
            "PySide6", "pydantic", "pydantic_settings", "httpx", "rich", 
            "dotenv", "scapy", "PIL", "magic", "capstone", "pefile", 
            "elftools", "yara", "cryptography", "sympy", "gmpy2"
        ]
        
        for pkg in packages:
            spec = importlib.util.find_spec(pkg)
            installed = spec is not None
            version = "UNKNOWN"
            status = "NOT_INSTALLED"
            path = ""
            
            if installed:
                status = "PYTHON_AVAILABLE"
                if getattr(spec, "origin", None):
                    path = str(getattr(spec, "origin", ""))
                try:
                    meta_pkg = pkg
                    if pkg == "dotenv": meta_pkg = "python-dotenv"
                    elif pkg == "PIL": meta_pkg = "Pillow"
                    elif pkg == "magic": meta_pkg = "python-magic"
                    elif pkg == "elftools": meta_pkg = "pyelftools"
                    elif pkg == "yara": meta_pkg = "yara-python"
                    version = importlib.metadata.version(meta_pkg)
                except Exception:
                    pass
                    
            t = Tool(
                id=f"pkg_{pkg.lower()}",
                name=pkg,
                executable="",
                tool_type="PYTHON PACKAGE",
                status=status,
                path=path,
                version=version,
                detection_method="importlib"
            )
            self._add_tool(t)
            
    def _scan_executables(self) -> None:
        exe_map = {
            "Wireshark": {"names": ["wireshark.exe", "wireshark"], "args": ["-v"]},
            "TShark": {"names": ["tshark.exe", "tshark"], "args": ["-v"]},
            "Ghidra": {"names": ["ghidraRun.bat", "ghidraRun", "ghidraRun.exe"], "args": []},
            "GDB": {"names": ["gdb.exe", "gdb"], "args": ["--version"]},
            "Radare2": {"names": ["radare2.exe", "radare2", "r2.exe", "r2"], "args": ["-v"]},
            "Volatility": {"names": ["vol.exe", "volatility.exe", "vol.py", "vol"], "args": ["-h"]},
            "ExifTool": {"names": ["exiftool.exe", "exiftool"], "args": ["-ver"]},
            "Binwalk": {"names": ["binwalk.exe", "binwalk"], "args": []},
            "YARA (CLI)": {"names": ["yara.exe", "yara32.exe", "yara64.exe", "yara"], "args": ["-v"]},
            "Stegseek": {"names": ["stegseek.exe", "stegseek"], "args": ["--version"]},
            "zsteg": {"names": ["zsteg", "zsteg.bat", "zsteg.cmd"], "args": ["--version"]},
            "strings": {"names": ["strings.exe", "strings"], "args": ["--version"]},
            "file": {"names": ["file.exe", "file"], "args": ["--version"]}
        }
        
        common_paths = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.environ.get("LOCALAPPDATA", ""),
            os.environ.get("APPDATA", ""),
            os.path.join(os.environ.get("USERPROFILE", ""), "bin"),
            os.path.join(os.environ.get("USERPROFILE", ""), "tools"),
            os.path.join(os.environ.get("USERPROFILE", ""), "scoop", "shims"),
            os.path.join(os.environ.get("USERPROFILE", ""), "scoop", "apps")
        ]
        common_paths = [p for p in common_paths if p and os.path.exists(p)]
        
        for name, config in exe_map.items():
            path_found = None
            method = "shutil.which"
            
            # Check configured path first if implemented in future
            # Then check PATH
            for exe in config["names"]:
                res = shutil.which(exe)
                if res:
                    path_found = res
                    break
                    
            # Check common directories
            if not path_found:
                for base in common_paths:
                    if path_found: break
                    for exe in config["names"]:
                        potential = os.path.join(base, exe)
                        if os.path.isfile(potential):
                            path_found = potential
                            method = "common_paths_scan"
                            break
                        # Also check some specific subfolders
                        if "wireshark" in name.lower() and os.path.exists(os.path.join(base, "Wireshark")):
                            potential = os.path.join(base, "Wireshark", exe)
                            if os.path.isfile(potential):
                                path_found = potential
                                method = "common_paths_scan"
                                break

            status = "NOT_INSTALLED"
            version = "UNKNOWN"
            if path_found:
                status = "AVAILABLE"
                if config["args"]:
                    try:
                        out = subprocess.check_output([path_found] + config["args"], stderr=subprocess.STDOUT, timeout=2, text=True)
                        lines = out.split("\n")
                        if lines:
                            # Just grab a snippet for version
                            v = lines[0].strip()
                            version = v[:30] + ("..." if len(v)>30 else "")
                    except Exception:
                        status = "VERSION_UNKNOWN"
                else:
                    status = "AVAILABLE"
            
            t = Tool(
                id=f"ext_{name.lower().replace(' ', '_')}",
                name=name,
                executable=config["names"][0],
                tool_type="EXTERNAL EXECUTABLE",
                status=status,
                path=path_found if path_found else "",
                version=version,
                detection_method=method if path_found else "None"
            )
            self._add_tool(t)

tool_service = ToolService()


