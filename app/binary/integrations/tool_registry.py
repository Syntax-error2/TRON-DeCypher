import shutil


class BinaryToolRegistry:
    """Detects optional external reverse engineering tools."""
    
    def check_tools(self) -> dict[str, bool]:
        return {
            "gdb": shutil.which("gdb") is not None,
            "ghidra": shutil.which("ghidraRun") is not None or shutil.which("analyzeHeadless") is not None,
            "radare2": shutil.which("radare2") is not None or shutil.which("r2") is not None,
            "rizin": shutil.which("rizin") is not None
        }

binary_tool_registry = BinaryToolRegistry()
