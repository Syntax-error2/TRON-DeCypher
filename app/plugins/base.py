from abc import ABC, abstractmethod
from typing import Any


class PluginBase(ABC):
    """Base interface for all TRON-DeCypher plugins."""
    
    name: str = "BasePlugin"
    version: str = "0.1.0"
    category: str = "general"
    description: str = "Base plugin"
    supported_input_types: list[str] = []
    dependencies: list[str] = []
    
    @abstractmethod
    def check_availability(self) -> bool:
        """Check if all requirements (tools, API keys) are met."""
        
    @abstractmethod
    def validate(self, input_data: Any) -> bool:
        """Validate if this plugin can handle the given input."""
        
    @abstractmethod
    def run(self, input_data: Any, context: dict[str, Any]) -> Any:
        """Execute the plugin logic."""
