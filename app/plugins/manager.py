import logging

from app.plugins.base import PluginBase
from app.plugins.registry import registry

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages discovery, initialization, and execution of plugins."""
    
    def __init__(self) -> None:
        self.active_plugins: dict[str, PluginBase] = {}
        
    def discover_plugins(self) -> None:
        """Scan and register plugins from the plugin directories.
        (Placeholder for Phase 1)
        """
        logger.info("Discovering plugins...")
        # In the future, dynamically import modules in analyzers, decoders, etc.
        
    def initialize_plugins(self) -> None:
        """Instantiate and verify availability of registered plugins."""
        for name, plugin_cls in registry.list_plugins().items():
            try:
                instance = plugin_cls()
                if instance.check_availability():
                    self.active_plugins[name] = instance
                    logger.debug(f"Plugin initialized: {name}")
                else:
                    logger.warning(f"Plugin {name} is not available (missing dependencies).")
            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {e}")
                
    def get_available_plugins(self) -> list[PluginBase]:
        """Return a list of initialized and available plugins."""
        return list(self.active_plugins.values())
