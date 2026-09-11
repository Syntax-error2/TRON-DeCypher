import sys
import re

with open("app/decoders/symbols/solver.py", "r", encoding="utf8") as f:
    text = f.read()

# freqs: dict[str, int] = {}
text = text.replace("freqs = {}", "freqs: dict[str, int] = {}")

# lambda x: x["score"] => candidates.sort(key=lambda x: float(x["score"]), reverse=True)
text = text.replace("candidates.sort(key=lambda x: x[\"score\"], reverse=True)", "candidates.sort(key=lambda x: float(str(x[\"score\"])), reverse=True)")

with open("app/decoders/symbols/solver.py", "w", encoding="utf8") as f:
    f.write(text)

with open("app/decoders/symbols/__init__.py", "r", encoding="utf8") as f:
    text = f.read()
    
text = text.replace("def __init__(self):", "def __init__(self) -> None:")
text = text.replace("def _load_profiles(self):", "def _load_profiles(self) -> None:")
text = text.replace("def analyze_image(self, image_path: str, profile_id: str = \"auto\", custom_mapping: dict[str, str] = None) -> SymbolResult:", "def analyze_image(self, image_path: str, profile_id: str = \"auto\", custom_mapping: dict[str, str] | None = None) -> SymbolResult:")

with open("app/decoders/symbols/__init__.py", "w", encoding="utf8") as f:
    f.write(text)

with open("tests/unit/test_symbol_decoder.py", "r", encoding="utf8") as f:
    text = f.read()
    
text = text.replace("def create_synthetic_image():", "def create_synthetic_image() -> Image.Image:")
text = text.replace("def test_", "def test_").replace("():\n", "() -> None:\n")
text = text.replace("counts = {}", "counts: dict[str, int] = {}")
text = text.replace("id_freq = {}", "id_freq: dict[str, int] = {}")

with open("tests/unit/test_symbol_decoder.py", "w", encoding="utf8") as f:
    f.write(text)
    
