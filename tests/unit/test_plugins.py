from typing import Any

from app.plugins.base import PluginBase
from app.plugins.registry import PluginRegistry


class DummyPlugin(PluginBase):
    name = "dummy"
    def check_availability(self) -> bool: return True
    def validate(self, input_data: Any) -> bool: return True
    def run(self, input_data: Any, context: Any) -> Any: return "ok"

def test_plugin_registry() -> None:
    registry = PluginRegistry()
    registry.register(DummyPlugin)
    
    assert "dummy" in registry.list_plugins()
    plugin_cls = registry.get_plugin("dummy")
    assert plugin_cls == DummyPlugin
