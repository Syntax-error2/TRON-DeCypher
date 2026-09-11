import json
import os
import shutil

from app.services.tool_execution_service import ToolExecutionRequest, tool_execution_service


class VolatilityIntegrationService:
    """Manages integration with Volatility 3 via ToolExecutionService."""
    
    def __init__(self) -> None:
        self.vol_path = self._find_volatility()
        
    def _find_volatility(self) -> str | None:
        for name in ["volatility3", "vol.py", "vol"]:
            path = shutil.which(name)
            if path:
                return path
        return None
        
    def is_available(self) -> bool:
        return self.vol_path is not None
        
    def run_plugin(self, memory_file: str, plugin: str) -> list[dict[str, object]] | None:
        """Executes a volatility plugin returning structured JSON."""
        if not self.is_available() or not self.vol_path:
            return None
            
        if not os.path.exists(memory_file):
            return None
            
        req = ToolExecutionRequest(
            executable=self.vol_path,
            arguments=["-f", memory_file, "-r", "json", plugin],
            working_directory=os.path.dirname(memory_file) or ".",
            timeout_seconds=300.0 # Volatility can be slow
        )
        
        res = tool_execution_service.run_tool(req)
        
        if res.status != "SUCCESS":
            return None
            
        try:
            # Volatility 3 typically outputs an array of JSON objects when -r json is used
            # Sometimes it outputs lines. We'll try to parse the whole stdout.
            data = json.loads(res.stdout)
            if isinstance(data, list):
                return data
            return [data]
        except json.JSONDecodeError:
            # Fallback if there's header text before the json
            try:
                # Naive search for first bracket
                start = res.stdout.find('[')
                end = res.stdout.rfind(']')
                if start != -1 and end != -1:
                    clean = res.stdout[start:end+1]
                    data = json.loads(clean)
                    if isinstance(data, list):
                        return data
            except Exception:
                pass
                
        return None

volatility_integration_service = VolatilityIntegrationService()
