import sys

from PIL import Image

from app.decoders.symbols.models import SymbolBoundingBox, SymbolItem

# Increase recursion depth for large connected components
sys.setrecursionlimit(50000)

class ImageSegmenter:
    def __init__(self, max_pixels: int = 2000000):
        self.max_pixels = max_pixels

    def segment(self, image: Image.Image) -> list[SymbolItem]:
        # Limit size
        if image.width * image.height > self.max_pixels:
            ratio = (self.max_pixels / (image.width * image.height)) ** 0.5
            new_w = int(image.width * ratio)
            new_h = int(image.height * ratio)
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
        # Convert to grayscale
        gray = image.convert("L")
        
        # Binarize via Otsu-ish or simple mean threshold
        pixels = list(gray.getdata())
        mean_val = sum(pixels) / len(pixels)
        threshold = int(mean_val * 0.9) # Slightly biased to capture ink
        
        # Create binary matrix: True if ink (dark), False if background (light)
        # We assume black symbols on white background or vice versa based on corners.
        corners = [pixels[0], pixels[image.width - 1], 
                   pixels[(image.height - 1) * image.width], pixels[-1]]
        bg_val = sum(corners) / 4
        invert = bg_val < 128
        
        w, h = gray.width, gray.height
        binary = [[False]*w for _ in range(h)]
        for y in range(h):
            for x in range(w):
                idx = y * w + x
                val = pixels[idx]
                if invert:
                    binary[y][x] = val > threshold
                else:
                    binary[y][x] = val < threshold
                    
        # Connected Components using BFS to prevent stack overflow
        visited = [[False]*w for _ in range(h)]
        boxes = []
        
        for y in range(h):
            for x in range(w):
                if binary[y][x] and not visited[y][x]:
                    # BFS
                    queue = [(x, y)]
                    visited[y][x] = True
                    min_x, max_x = x, x
                    min_y, max_y = y, y
                    pts_count = 0
                    
                    head = 0
                    while head < len(queue):
                        cx, cy = queue[head]
                        head += 1
                        pts_count += 1
                        
                        min_x = min(min_x, cx)
                        max_x = max(max_x, cx)
                        min_y = min(min_y, cy)
                        max_y = max(max_y, cy)
                        
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if binary[ny][nx] and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                                    
                    # Filter out tiny noise (e.g. less than 10 pixels or 2x2 bounding box)
                    if pts_count > 10 and (max_x - min_x) > 2 and (max_y - min_y) > 2:
                        # Add some padding
                        px1 = max(0, min_x - 2)
                        py1 = max(0, min_y - 2)
                        px2 = min(w, max_x + 3)
                        py2 = min(h, max_y + 3)
                        boxes.append(SymbolBoundingBox(px1, py1, px2 - px1, py2 - py1))
                        
        # Merge highly overlapping bounding boxes (fixes disconnected parts of same symbol)
        merged = True
        while merged:
            merged = False
            for i in range(len(boxes)):
                for j in range(i+1, len(boxes)):
                    b1, b2 = boxes[i], boxes[j]
                    # Check overlap
                    if not (b1.x > b2.x + b2.w or b2.x > b1.x + b1.w or b1.y > b2.y + b2.h or b2.y > b1.y + b1.h):
                        # Merge b2 into b1
                        nx1 = min(b1.x, b2.x)
                        ny1 = min(b1.y, b2.y)
                        nx2 = max(b1.x + b1.w, b2.x + b2.w)
                        ny2 = max(b1.y + b1.h, b2.y + b2.h)
                        boxes[i] = SymbolBoundingBox(nx1, ny1, nx2 - nx1, ny2 - ny1)
                        boxes.pop(j)
                        merged = True
                        break
                if merged:
                    break

        items = []
        for b in boxes:
            crop = gray.crop((b.x, b.y, b.x + b.w, b.y + b.h))
            items.append(SymbolItem(bbox=b, crop=crop))
            
        return items

segmenter = ImageSegmenter()
