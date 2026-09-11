import hashlib
import os
from typing import Any

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

class ImageAnalyzerService:
    def analyze(self, file_path: str) -> dict[str, Any]:
        result = {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "sha256": "",
            "format": "Unknown",
            "dimensions": "Unknown",
            "has_pillow": HAS_PILLOW,
            "ocr_available": False, # Mock
            "qr_detected": 0, # Mock
            "stego_potential": "None detected", # Mock
            "embedded_data": "None detected", # Mock
            "iocs_count": 0, # Mock
        }
        
        with open(file_path, "rb") as f:
            data = f.read()
            result["sha256"] = hashlib.sha256(data).hexdigest()
            
            # Simple magic number detection
            if data.startswith(b"\x89PNG\r\n\x1a\n"):
                result["format"] = "PNG"
            elif data.startswith(b"\xff\xd8"):
                result["format"] = "JPEG"
            elif data.startswith(b"GIF87a") or data.startswith(b"GIF89a"):
                result["format"] = "GIF"
            elif data.startswith(b"BM"):
                result["format"] = "BMP"

        if HAS_PILLOW:
            try:
                with Image.open(file_path) as img:
                    result["dimensions"] = f"{img.width} x {img.height}"
                    if result["format"] == "Unknown":
                        result["format"] = img.format or "Unknown"
            except Exception:
                pass
                
        return result

image_analyzer_service = ImageAnalyzerService()
