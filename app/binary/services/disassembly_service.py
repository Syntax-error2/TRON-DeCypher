from app.binary.models import DisassembledInstruction

try:
    import capstone
    HAS_CAPSTONE = True
except ImportError:
    HAS_CAPSTONE = False

class DisassemblyService:
    """Safely disassembles small binary blocks using Capstone."""
    
    # Hard limit to prevent memory exhaustion
    MAX_BYTES = 4096 
    
    def disassemble(self, data: bytes, architecture: str, base_address: int) -> list[DisassembledInstruction]:
        if not HAS_CAPSTONE:
            raise RuntimeError("Capstone is not installed.")
            
        if len(data) > self.MAX_BYTES:
            data = data[:self.MAX_BYTES]
            
        arch = capstone.CS_ARCH_X86
        mode = capstone.CS_MODE_64
        
        arch_lower = architecture.lower()
        if "x86" in arch_lower and not "64" in arch_lower:
            mode = capstone.CS_MODE_32
        elif "arm64" in arch_lower or "aarch64" in arch_lower:
            arch = capstone.CS_ARCH_ARM64
            mode = capstone.CS_MODE_ARM
        elif "arm" in arch_lower:
            arch = capstone.CS_ARCH_ARM
            mode = capstone.CS_MODE_ARM
            
        instructions = []
        md = capstone.Cs(arch, mode)
        
        for i in md.disasm(data, base_address):
            instructions.append(DisassembledInstruction(
                address=i.address,
                bytes_hex=i.bytes.hex(),
                mnemonic=i.mnemonic,
                operands=i.op_str
            ))
            
        return instructions

disassembly_service = DisassemblyService()
