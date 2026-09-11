import os


class InputAnalysisRouter:
    def route_file(self, file_path: str) -> str:
        """Determines the primary category for a given file."""
        if not os.path.exists(file_path):
            return "UNKNOWN"
            
        ext = file_path.lower().split('.')[-1]
        
        # Image
        if ext in ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp', 'tiff']:
            return "IMAGE"
            
        # PCAP
        if ext in ['pcap', 'pcapng']:
            return "PCAP"
            
        # Binary / Executable
        if ext in ['exe', 'dll', 'sys', 'elf', 'bin']:
            return "BINARY"
            
        # Archive
        if ext in ['zip', 'rar', '7z', 'tar', 'gz']:
            return "ARCHIVE"
            
        # Memory
        if ext in ['raw', 'mem', 'vmem', 'dmp']:
            return "MEMORY"
            
        # Text/Default
        if ext in ['txt', 'md', 'json', 'xml', 'csv', 'log']:
            return "TEXT"
            
        return "FILE"

input_router = InputAnalysisRouter()
