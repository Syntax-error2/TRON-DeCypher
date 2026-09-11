import logging
import sys

from PySide6.QtWidgets import QApplication

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.paths import ensure_directories
from app.database.database import db
from app.services.tool_service import tool_service


def main() -> None:
    # 1. Initialize paths
    ensure_directories()
    
    # 2. Initialize logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # 3. Initialize SQLite
    try:
        db.initialize()
    except Exception as e:
        logger.critical(f"Failed to initialize database: {e}")
        sys.exit(1)
        
    # 4. Initialize plugin registry
    from app.decoders import register_all_decoders
    from app.plugins.manager import PluginManager
    plugin_manager = PluginManager()
    plugin_manager.discover_plugins()
    register_all_decoders()
    plugin_manager.initialize_plugins()
    
    # 5. Initialize tool registry
    tool_service.scan_for_tools()
    
    # 6. Start PySide6 application
    app = QApplication(sys.argv)
    app.setApplicationName(settings.app_name)
    app.setApplicationVersion(settings.app_version)
    
    # 7. Display Main Window
    # Import here to avoid loading Qt before app is created if imported at top
    from app.ui.main_window import MainWindow
    window = MainWindow()
    window.show()
    
    # 8. Exit cleanly
    logger.info("Application event loop started.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
