import logging
from pathlib import Path

from app.services.text_analysis_service import text_analysis_service
from app.stego.models import StegoExtractionResult

logger = logging.getLogger(__name__)

class LSBAnalyzer:
    """Performs LSB (Least Significant Bit) extraction on images."""
    
    def analyze(self, file_path: Path) -> list[StegoExtractionResult]:
        """Extracts bit 0 from RGB channels and analyzes it for text."""
        results = []
        try:
            import numpy as np
            from PIL import Image
            
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                arr = np.array(img)
                
                channels = {'R': arr[:,:,0], 'G': arr[:,:,1], 'B': arr[:,:,2]}
                
                for ch_name, ch_data in channels.items():
                    # Extract LSB (bit 0)
                    lsbs = ch_data & 1
                    
                    # Flatten and pack bits into bytes
                    flat = lsbs.flatten()
                    # Ensure multiple of 8
                    pad = len(flat) % 8
                    if pad != 0:
                        flat = flat[:-pad]
                        
                    # This is slow in pure python, but np.packbits is fast
                    extracted_bytes = np.packbits(flat).tobytes()
                    
                    analysis = text_analysis_service.analyze(extracted_bytes)
                    
                    if analysis["printable_ratio"] > 0.01: # Even 1% might contain a hidden flag in a big image
                        try:
                            # Try decoding as ascii for printable preview
                            text_preview = ""
                            import string
                            printable = set(string.printable.encode('ascii'))
                            for b in extracted_bytes:
                                if b in printable:
                                    text_preview += chr(b)
                                    
                            if len(text_preview) > 10:
                                results.append(StegoExtractionResult(
                                    analyzer="LSB-0",
                                    channel=ch_name,
                                    extracted_text=text_preview,
                                    extracted_bytes=extracted_bytes,
                                    metadata={"printable_ratio": analysis["printable_ratio"]}
                                ))
                        except Exception:
                            pass
                            
        except ImportError:
            logger.warning("Pillow or numpy not installed. Stego LSB unavailable.")
        except Exception as e:
            logger.error(f"LSB analysis failed: {e}")
            
        return results
