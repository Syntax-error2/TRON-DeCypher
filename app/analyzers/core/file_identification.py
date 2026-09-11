import logging
import mimetypes
from pathlib import Path
from typing import Any

from app.plugins.base import PluginBase

logger = logging.getLogger(__name__)

class FileIdentificationAnalyzer(PluginBase):
    name = "file_identification"
    version = "1.0.0"
    category = "core"
    description = "Identifies file types using signatures and metadata."
    supported_input_types = ["file"]
    
    def check_availability(self) -> bool:
        return True
        
    def validate(self, input_data: Any) -> bool:
        return isinstance(input_data, (str, Path)) and Path(input_data).is_file()
        
    def run(self, input_data: Any, context: dict[str, Any]) -> dict[str, Any]:
        path = Path(input_data)
        
        # Basic OS identification
        mime_type, encoding = mimetypes.guess_type(str(path))
        extension = path.suffix.lower()
        size = path.stat().st_size
        
        magic_desc = "Unknown"
        magic_mime = None
        
        # Optional python-magic integration
        try:
            import magic
            # Try to get both mime type and description if available
            try:
                magic_desc = magic.from_file(str(path))
                magic_mime = magic.from_file(str(path), mime=True)
            except Exception as e:
                logger.debug(f"python-magic failed to read {path}: {e}")
        except ImportError:
            logger.debug("python-magic not installed, falling back to mimetypes.")
            
        # Fallback / Custom magic byte checks
        try:
            with open(path, 'rb') as f:
                header = f.read(4)
                if header in (b'\xd4\xc3\xb2\xa1', b'\xa1\xb2\xc3\xd4', b'\xd4\x3c\xb2\xa1', b'\xa1\xb2\x3c\xd4'):
                    if magic_desc == "Unknown":
                        magic_desc = "tcpdump capture file (pcap)"
                        magic_mime = "application/vnd.tcpdump.pcap"
                elif header == b'\x0a\x0d\x0d\x0a' and magic_desc == "Unknown":
                    magic_desc = "pcapng capture file"
                    magic_mime = "application/x-pcapng"
        except Exception as e:
            logger.debug(f"Raw magic check failed: {e}")
            
        return {
            "extension": extension,
            "mime_type_os": mime_type,
            "mime_type_magic": magic_mime,
            "magic_description": magic_desc,
            "size_bytes": size,
            "encoding": encoding
        }
