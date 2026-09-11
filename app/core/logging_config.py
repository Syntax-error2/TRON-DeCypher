import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

from app.core.config import settings


def setup_logging() -> None:
    """Initialize centralized logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # Formatting
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console Handler (Rich)
    console_handler = RichHandler(rich_tracebacks=True, show_path=False)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File Handler
    log_file = Path(settings.logs_path) / "tron_decypher.log"
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Avoid logging overly verbose third-party logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("pydantic").setLevel(logging.WARNING)

    logging.info(f"Logging initialized at {settings.log_level} level.")
