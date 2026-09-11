import uuid

from PIL import Image

from app.decoders.symbols.models import SymbolItem


class SymbolRecognizer:
    def __init__(self, match_threshold: float = 0.15, norm_size: tuple[int, int] = (16, 16)):
        self.match_threshold = match_threshold
        self.norm_size = norm_size
        
    def _mse(self, img1: Image.Image, img2: Image.Image) -> float:
        i1 = img1.resize(self.norm_size, Image.Resampling.BILINEAR)
        i2 = img2.resize(self.norm_size, Image.Resampling.BILINEAR)
        p1 = list(i1.getdata())
        p2 = list(i2.getdata())
        err = sum((a - b)**2 for a, b in zip(p1, p2)) / float(len(p1) * 255 * 255)
        return err

    def group_symbols(self, symbols: list[SymbolItem]) -> None:
        groups = [] # list of (group_id, representative_img)
        
        for idx, item in enumerate(symbols):
            matched = False
            best_mse = float('inf')
            best_group = None
            
            for gid, rep in groups:
                mse = self._mse(item.crop, rep)
                if mse < self.match_threshold and mse < best_mse:
                    best_mse = mse
                    best_group = gid
                    
            if best_group is not None:
                item.symbol_id = best_group
            else:
                new_id = f"sym_{uuid.uuid4().hex[:6]}"
                groups.append((new_id, item.crop))
                item.symbol_id = new_id

recognizer = SymbolRecognizer()
