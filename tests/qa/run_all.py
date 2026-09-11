import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

import tests.qa.qa_framework as qa

import glob
import importlib.util

def load_tests():
    test_files = glob.glob(str(Path(__file__).parent / "test_*.py"))
    for f in test_files:
        name = Path(f).stem
        spec = importlib.util.spec_from_file_location(name, f)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "run_tests"):
            mod.run_tests()

if __name__ == "__main__":
    load_tests()
    qa.export_results()
