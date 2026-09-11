import json
import os

from PIL import Image

from app.decoders.symbols.models import SymbolProfile, SymbolResult
from app.decoders.symbols.recognizer import recognizer
from app.decoders.symbols.segmenter import segmenter
from app.decoders.symbols.solver import solver


class SymbolAnalysisService:
    def __init__(self) -> None:
        self.profiles = {}
        self._load_profiles()
        
    def _load_profiles(self) -> None:
        profile_path = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge", "symbols", "profiles.json")
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.profiles[k] = SymbolProfile(id=k, name=v["name"], mapping=v.get("mapping", {}))
                    
    def get_profiles(self) -> dict[str, SymbolProfile]:
        return self.profiles
        
    def analyze_image(self, image_path: str, profile_id: str = "auto", custom_mapping: dict[str, str] | None = None) -> SymbolResult:
        try:
            img = Image.open(image_path)
            # Ensure RGB
            img = img.convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid image format: {e}")
            
        custom_mapping = custom_mapping or {}
        
        # 1. Segment
        symbols = segmenter.segment(img)
        
        # 2. Recognize / Group
        recognizer.group_symbols(symbols)
        
        # 3. Apply profile / mapping
        profile_mapping = {}
        if profile_id != "auto" and profile_id in self.profiles:
            profile_mapping = self.profiles[profile_id].mapping
            
        # 4. Solve
        result = solver.solve(symbols, custom_mapping, profile_mapping)
        result.profile = profile_id
        
        return result

symbol_analysis_service = SymbolAnalysisService()
