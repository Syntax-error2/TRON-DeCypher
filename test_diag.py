import sys
import os
sys.path.insert(0, os.path.abspath("."))
from app.services.tool_service import tool_service

tool_service.scan_for_tools()
for tool in tool_service.tools.values():
    print(f"{tool.name}: {tool.tool_type} -> {tool.status} ({tool.version})")
