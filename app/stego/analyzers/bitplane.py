import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class BitplaneAnalyzer:
    """Analyzes and isolates individual bit planes of an image."""
    
    def generate_bitplane_stats(self, file_path: Path) -> dict[str, Any]:
        """Calculates basic statistics for each bitplane."""
        stats: dict[str, Any] = {}
        try:
            import numpy as np
            from PIL import Image
            
            with Image.open(file_path) as img:
                img = img.convert("RGB")
                arr = np.array(img)
                
                channels = {'R': arr[:,:,0], 'G': arr[:,:,1], 'B': arr[:,:,2]}
                
                for ch_name, ch_data in channels.items():
                    stats[ch_name] = {}
                    for bit in range(8):
                        plane = (ch_data >> bit) & 1
                        zeros = np.count_nonzero(plane == 0)
                        ones = np.count_nonzero(plane == 1)
                        total = zeros + ones
                        if total > 0:
                            ratio = ones / total
                            stats[ch_name][f"bit_{bit}"] = {
                                "zeros": int(zeros),
                                "ones": int(ones),
                                "ones_ratio": float(ratio)
                            }
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Bitplane analysis failed: {e}")
            
        return stats
