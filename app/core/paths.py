import sys
from pathlib import Path

# Determine if running in a PyInstaller bundle
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # In PyInstaller, sys.executable is the .exe location
    APP_EXECUTABLE_DIR = Path(sys.executable).parent
    APP_ROOT = Path(sys._MEIPASS) / "app"
    PROJECT_ROOT = APP_EXECUTABLE_DIR
else:
    APP_ROOT = Path(__file__).resolve().parent.parent
    PROJECT_ROOT = APP_ROOT.parent

# Check for portable marker
IS_PORTABLE = (PROJECT_ROOT / ".portable").exists()

# In portable mode or frozen, everything is relative to the executable
# Otherwise, it's relative to the repo root
DATA_DIR = PROJECT_ROOT / "data"
CASES_DIR = PROJECT_ROOT / "cases"
LOGS_DIR = PROJECT_ROOT / "logs"
CONFIG_DIR = PROJECT_ROOT / "config"
TOOLS_DIR = PROJECT_ROOT / "tools"

def ensure_directories() -> None:
    for directory in [DATA_DIR, CASES_DIR, LOGS_DIR, CONFIG_DIR, TOOLS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

def get_database_path() -> Path:
    return DATA_DIR / "tron_decypher.sqlite"
