from dataclasses import dataclass
from pathlib import Path


@dataclass
class SignatureMatch:
    offset: int
    signature: bytes
    detected_type: str
    description: str

class FileSignatureAnalyzer:
    """Analyzes file signatures (magic bytes) to identify file types."""
    
    # Common signatures (offset, bytes, name, description)
    SIGNATURES = [
        (0, b'\xFF\xD8\xFF', 'JPEG', 'JPEG image data'),
        (0, b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', 'PNG', 'PNG image data'),
        (0, b'GIF87a', 'GIF', 'GIF image data (87a)'),
        (0, b'GIF89a', 'GIF', 'GIF image data (89a)'),
        (0, b'%PDF-', 'PDF', 'PDF document'),
        (0, b'PK\x03\x04', 'ZIP', 'ZIP archive data'),
        (0, b'Rar!\x1A\x07\x00', 'RAR', 'RAR archive data'),
        (0, b'Rar!\x1A\x07\x01\x00', 'RAR', 'RAR archive data (v5)'),
        (0, b'7z\xBC\xAF\x27\x1C', '7z', '7-zip archive data'),
        (0, b'\x1F\x8B', 'GZIP', 'GZIP compressed data'),
        (0, b'BM', 'BMP', 'BMP image data'),
        (0, b'RIFF', 'WAV', 'WAV audio data (starts with RIFF)'), # Needs more logic for precise WAV
        (0, b'ID3', 'MP3', 'MP3 audio data (ID3)'),
        (4, b'ftyp', 'MP4', 'MP4 video data'),
        (0, b'\x7FELF', 'ELF', 'ELF executable'),
        (0, b'MZ', 'PE', 'PE executable (Windows)'),
        (0, b'SQLite format 3\x00', 'SQLite', 'SQLite 3 database'),
    ]

    def analyze(self, file_path: Path, read_limit: int = 1024 * 1024) -> list[SignatureMatch]:
        """
        Scans a file for known signatures at expected offsets.
        By default scans the first 1MB for flexibility (some signatures aren't at 0).
        """
        matches = []
        try:
            with open(file_path, "rb") as f:
                data = f.read(read_limit)
                
            for expected_offset, sig, name, desc in self.SIGNATURES:
                # Check specific offset
                if expected_offset < len(data):
                    if data[expected_offset:expected_offset+len(sig)] == sig:
                        matches.append(SignatureMatch(
                            offset=expected_offset,
                            signature=sig,
                            detected_type=name,
                            description=desc
                        ))
        except Exception:
            pass
            
        return matches

    def check_mismatch(self, filename: str, matches: list[SignatureMatch]) -> str | None:
        """Checks if the file extension disagrees with the detected signature."""
        if not matches:
            return None
            
        ext = Path(filename).suffix.lower().replace('.', '')
        if not ext:
            return None
            
        # Map common extensions to signature names
        ext_map = {
            'jpg': 'JPEG', 'jpeg': 'JPEG',
            'png': 'PNG',
            'gif': 'GIF',
            'pdf': 'PDF',
            'zip': 'ZIP',
            'rar': 'RAR',
            '7z': '7z',
            'gz': 'GZIP',
            'bmp': 'BMP',
            'wav': 'WAV',
            'mp3': 'MP3',
            'mp4': 'MP4',
            'exe': 'PE', 'dll': 'PE',
            'so': 'ELF',
            'sqlite': 'SQLite', 'db': 'SQLite'
        }
        
        expected_type = ext_map.get(ext)
        if expected_type:
            # Check if any match matches the expected type
            if not any(m.detected_type == expected_type for m in matches):
                primary_match = matches[0].detected_type
                return f"File extension (.{ext}) does not match detected signature ({primary_match})."
                
        return None
