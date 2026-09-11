import datetime
import mimetypes
from pathlib import Path
from typing import Any


class MetadataAnalyzer:
    """Extracts file system and format metadata."""
    
    def analyze(self, file_path: Path) -> dict[str, Any]:
        """Extracts basic file metadata."""
        meta: dict[str, Any] = {}
        
        try:
            stat = file_path.stat()
            meta["size"] = stat.st_size
            meta["created"] = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()
            meta["modified"] = datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            meta["accessed"] = datetime.datetime.fromtimestamp(stat.st_atime).isoformat()
            
            mime, _ = mimetypes.guess_type(str(file_path))
            meta["mime_type"] = mime or "application/octet-stream"
            meta["filename"] = file_path.name
            meta["extension"] = file_path.suffix
            
            # Try to get EXIF/image data if Pillow is available
            img_meta = self._extract_image_metadata(file_path)
            if img_meta:
                meta["image"] = img_meta
                
        except Exception as e:
            meta["error"] = str(e)
            
        return meta
        
    def _extract_image_metadata(self, file_path: Path) -> dict[str, Any]:
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img_meta = {}
            with Image.open(file_path) as img:
                img_meta["format"] = img.format
                img_meta["mode"] = img.mode
                img_meta["width"], img_meta["height"] = img.size
                
                exif_data = img.getexif()
                if exif_data:
                    exif_dict = {}
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        # Filter out huge binary blobs like MakerNote
                        if isinstance(value, bytes):
                            if len(value) > 100:
                                value = f"<Binary data: {len(value)} bytes>"
                            else:
                                value = value.decode(errors='ignore')
                        exif_dict[str(tag)] = str(value)
                    img_meta["exif"] = exif_dict
            return img_meta
        except ImportError:
            return {} # Pillow not installed
        except Exception:
            return {} # Not an image or unparseable
