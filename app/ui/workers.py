import logging
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

class AnalysisWorker(QThread):
    """Executes a long-running analysis job in a separate thread."""
    
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, target: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        
    def run(self) -> None:
        try:
            logger.info("Background analysis started.")
            result = self.target(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Background analysis failed: {e}")
            self.error.emit(str(e))
