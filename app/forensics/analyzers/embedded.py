from dataclasses import dataclass
from pathlib import Path


@dataclass
class EmbeddedMatch:
    offset: int
    signature: bytes
    detected_type: str

class EmbeddedDataAnalyzer:
    """Scans for files embedded inside other files or appended to the EOF."""
    
    # Signatures to look for anywhere in the file (embedded archives/executables)
    SEARCH_SIGNATURES = [
        (b'PK\x03\x04', 'ZIP'),
        (b'Rar!\x1A\x07\x00', 'RAR'),
        (b'7z\xBC\xAF\x27\x1C', '7z'),
        (b'%PDF-', 'PDF'),
        (b'\x7FELF', 'ELF'),
    ]
    
    # EOF markers to find appended data
    EOF_MARKERS = {
        'JPEG': b'\xFF\xD9',
        'PNG': b'\x49\x45\x4E\x44\xAE\x42\x60\x82'
    }

    def analyze_embedded_signatures(self, file_path: Path, read_limit: int = 50 * 1024 * 1024) -> list[EmbeddedMatch]:
        """Scans the file for common signatures starting at non-zero offsets."""
        matches = []
        try:
            with open(file_path, "rb") as f:
                data = f.read(read_limit)
                
            for sig, name in self.SEARCH_SIGNATURES:
                offset = 1 # Start past 0
                while True:
                    idx = data.find(sig, offset)
                    if idx == -1:
                        break
                    matches.append(EmbeddedMatch(offset=idx, signature=sig, detected_type=name))
                    offset = idx + len(sig)
        except Exception:
            pass
            
        return matches

    def check_appended_data(self, file_path: Path, expected_type: str, read_limit: int = 50 * 1024 * 1024) -> int | None:
        """
        Checks if there is data after the expected EOF marker.
        Returns the offset of the appended data if found.
        """
        marker = self.EOF_MARKERS.get(expected_type)
        if not marker:
            return None
            
        try:
            with open(file_path, "rb") as f:
                data = f.read(read_limit)
                
            # Find the last occurrence of the EOF marker
            idx = data.rfind(marker)
            if idx != -1:
                end_of_file = idx + len(marker)
                # If there is data after the marker (ignoring trailing newlines/nulls)
                trailing_data = data[end_of_file:].strip(b'\x00\r\n')
                if len(trailing_data) > 0:
                    return end_of_file
        except Exception:
            pass
            
        return None
