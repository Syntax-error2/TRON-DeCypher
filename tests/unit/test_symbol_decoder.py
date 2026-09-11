from PIL import Image, ImageDraw

from app.decoders.symbols import symbol_analysis_service
from app.decoders.symbols.direction import direction_analyzer
from app.decoders.symbols.models import SymbolBoundingBox, SymbolItem
from app.decoders.symbols.recognizer import recognizer
from app.decoders.symbols.segmenter import segmenter
from app.decoders.symbols.solver import solver


def create_synthetic_image() -> Image.Image:
    # Create a 200x100 white image
    img = Image.new('RGB', (200, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a sequence of identical boxes and some different ones
    # Row 1 (y=20 to 40)
    # Box A: solid black 20x20
    draw.rectangle([10, 20, 30, 40], fill='black')
    # Box B: empty black outline 20x20
    draw.rectangle([40, 20, 60, 40], fill='white', outline='black', width=3)
    # Box A again
    draw.rectangle([70, 20, 90, 40], fill='black')
    
    # Row 2 (y=60 to 80)
    # Box C: small circle
    draw.ellipse([15, 65, 25, 75], fill='black')
    # Box A again
    draw.rectangle([40, 60, 60, 80], fill='black')
    
    return img

def test_segmenter() -> None:
    img = create_synthetic_image()
    symbols = segmenter.segment(img)
    assert len(symbols) == 5
    assert any(abs(s.bbox.center[1] - 30) < 5 for s in symbols)

def test_recognizer() -> None:
    img = create_synthetic_image()
    symbols = segmenter.segment(img)
    recognizer.group_symbols(symbols)
    
    unique_ids = set(s.symbol_id for s in symbols)
    assert len(unique_ids) == 3
    
    counts: dict[str, int] = {}
    for s in symbols:
        counts[s.symbol_id] = counts.get(s.symbol_id, 0) + 1
        
    assert 3 in counts.values()
    assert 1 in counts.values()
    
def test_direction_lr() -> None:
    img = create_synthetic_image()
    symbols = segmenter.segment(img)
    sorted_syms = direction_analyzer.sort_symbols(symbols, "lr")
    xs = [s.bbox.center[0] for s in sorted_syms]
    assert xs[0] < xs[1] < xs[2]
    assert xs[3] < xs[4]
    
def test_solver_custom_mapping() -> None:
    img = create_synthetic_image()
    symbols = segmenter.segment(img)
    recognizer.group_symbols(symbols)
    
    sorted_syms = direction_analyzer.sort_symbols(symbols, "lr")
    
    id_freq: dict[str, int] = {}
    for s in sorted_syms:
        id_freq[s.symbol_id] = id_freq.get(s.symbol_id, 0) + 1
        
    id_a = next(k for k, v in id_freq.items() if v == 3)
    id_b = sorted_syms[1].symbol_id
    id_c = sorted_syms[3].symbol_id
    
    custom_map = {
        id_a: "A",
        id_b: "B",
        id_c: "C"
    }
    
    res = solver.solve(symbols, custom_mapping=custom_map)
    assert res.unique_symbols == 3
    best = [c for c in res.candidates if c["direction"] == "lr" and c["type"] == "mapped"]
    assert len(best) > 0
    assert best[0]["text"] == "ABACA"

def test_auto_solve_ctf_flag() -> None:
    # Mocking symbols to test just the solver logic
    dummy_img = Image.new('RGB', (10, 10))
    symbols = [
        SymbolItem(bbox=SymbolBoundingBox(10, 20, 10, 10), crop=dummy_img, symbol_id="id1"),
        SymbolItem(bbox=SymbolBoundingBox(30, 20, 10, 10), crop=dummy_img, symbol_id="id2"),
        SymbolItem(bbox=SymbolBoundingBox(50, 20, 10, 10), crop=dummy_img, symbol_id="id3"),
        SymbolItem(bbox=SymbolBoundingBox(70, 20, 10, 10), crop=dummy_img, symbol_id="id4"),
        SymbolItem(bbox=SymbolBoundingBox(90, 20, 10, 10), crop=dummy_img, symbol_id="id5"),
        SymbolItem(bbox=SymbolBoundingBox(110, 20, 10, 10), crop=dummy_img, symbol_id="id6"),
    ]
    
    sorted_syms = direction_analyzer.sort_symbols(symbols, "lr")
    
    custom_map = {
        "id1": "C",
        "id2": "T",
        "id3": "K",
        "id4": "{",
        "id5": "A",
        "id6": "}"
    }
    
    res = solver.solve(symbols, custom_mapping=custom_map)
    best = res.candidates[0]
    assert best["text"] == "CTK{A}"
    assert best["score"] >= 5.0 # Gets the flag boost
from PIL import Image


def test_output_type_safety(tmp_path):
    img_path = str(tmp_path / "test_image.png")
    img = Image.new('RGB', (100, 100), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([10, 10, 20, 20], fill='black')
    img.save(img_path)
    
    # We want to ensure analyze_image doesn't return the image or path as best candidate
    res = symbol_analysis_service.analyze_image(img_path)
    
    # Verify the result object has a string representation
    if res.candidates:
        assert res.best_candidate != img_path, "Output must not be the image path"
        assert isinstance(res.best_candidate, str), "Output text must be string"
