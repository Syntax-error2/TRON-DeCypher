import binascii
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PngChunk:
    offset: int
    length: int
    type: str
    crc_ok: bool
    is_known: bool

class ImageAnalyzer:
    """Performs deep structural analysis of image formats."""
    
    KNOWN_PNG_CHUNKS = {
        'IHDR', 'PLTE', 'IDAT', 'IEND', 'tRNS', 'cHRM', 'gAMA', 'iCCP', 
        'sBIT', 'sRGB', 'tEXt', 'zTXt', 'iTXt', 'bKGD', 'hIST', 'pHYs', 'sPLT', 'tIME'
    }
    
    def analyze_png(self, file_path: Path) -> list[PngChunk]:
        """Parses a PNG file and returns a list of its chunks."""
        chunks: list[PngChunk] = []
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
                if header != b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A':
                    return chunks
                    
                offset = 8
                while True:
                    length_bytes = f.read(4)
                    if len(length_bytes) < 4:
                        break # EOF
                        
                    length = struct.unpack(">I", length_bytes)[0]
                    type_bytes = f.read(4)
                    if len(type_bytes) < 4:
                        break
                        
                    chunk_type = type_bytes.decode('ascii', errors='replace')
                    
                    data = f.read(length)
                    if len(data) < length:
                        break
                        
                    crc_bytes = f.read(4)
                    if len(crc_bytes) < 4:
                        break
                        
                    expected_crc = struct.unpack(">I", crc_bytes)[0]
                    actual_crc = binascii.crc32(type_bytes + data) & 0xFFFFFFFF
                    
                    chunks.append(PngChunk(
                        offset=offset,
                        length=length,
                        type=chunk_type,
                        crc_ok=(expected_crc == actual_crc),
                        is_known=(chunk_type in self.KNOWN_PNG_CHUNKS)
                    ))
                    
                    offset += 12 + length
        except Exception:
            pass
            
        return chunks
        
    def analyze_jpeg_markers(self, file_path: Path) -> list[dict[str, Any]]:
        """Parses basic JPEG markers."""
        markers: list[dict[str, Any]] = []
        try:
            with open(file_path, "rb") as f:
                data = f.read()
                
            if not data.startswith(b'\xFF\xD8'):
                return markers
                
            offset = 2
            while offset < len(data) - 1:
                if data[offset] == 0xFF:
                    marker_type = data[offset+1]
                    if marker_type == 0x00 or marker_type == 0xFF:
                        offset += 1
                        continue
                        
                    marker_name = hex(marker_type)
                    length = 0
                    if marker_type not in (0xD8, 0xD9, 0x01, 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7):
                        if offset + 3 < len(data):
                            length = struct.unpack(">H", data[offset+2:offset+4])[0]
                            
                    markers.append({
                        "offset": offset,
                        "marker": marker_name,
                        "length": length
                    })
                    
                    if length > 0:
                        offset += 2 + length
                    else:
                        offset += 2
                        if marker_type == 0xDA: # SOS (Start of Scan), stream follows
                            break
                else:
                    offset += 1
        except Exception:
            pass
            
        return markers
