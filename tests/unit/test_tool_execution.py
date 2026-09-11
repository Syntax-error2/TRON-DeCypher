import sys

from app.services.tool_execution_service import ToolExecutionRequest, tool_execution_service


def test_tool_execution() -> None:
    # Use python itself as a tool to echo a string
    req = ToolExecutionRequest(
        executable=sys.executable,
        arguments=["-c", "print('hello world')"],
        working_directory="."
    )
    
    result = tool_execution_service.run_tool(req)
    
    assert result.status == "SUCCESS"
    assert result.exit_code == 0
    assert "hello world" in result.stdout
    assert result.duration > 0
    
def test_tool_execution_timeout() -> None:
    req = ToolExecutionRequest(
        executable=sys.executable,
        arguments=["-c", "import time; time.sleep(2)"],
        working_directory=".",
        timeout_seconds=0.5
    )
    
    result = tool_execution_service.run_tool(req)
    
    assert result.status == "TIMEOUT"
    assert result.exit_code == -1
