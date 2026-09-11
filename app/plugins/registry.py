import logging

from app.plugins.base import PluginBase

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Registry for all available plugins."""
    
    def __init__(self) -> None:
        self._plugins: dict[str, type[PluginBase]] = {}
        
    def register(self, plugin_class: type[PluginBase]) -> None:
        """Register a new plugin class."""
        self._plugins[plugin_class.name] = plugin_class
        logger.debug(f"Registered plugin: {plugin_class.name}")
        
    def get_plugin(self, name: str) -> type[PluginBase]:
        """Retrieve a plugin class by name."""
        return self._plugins[name]
        
    def list_plugins(self) -> dict[str, type[PluginBase]]:
        """List all registered plugins."""
        return self._plugins

registry = PluginRegistry()
