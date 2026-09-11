import logging
import subprocess
import time

from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ToolExecutionRequest(BaseModel):
    executable: str
    arguments: list[str]
    working_directory: str
    timeout_seconds: float = 60.0
    
class ToolExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    status: str # SUCCESS, ERROR, TIMEOUT
    
class ToolExecutionService:
    """Safe execution service for external analysis tools."""
    
    def run_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Executes a local tool safely."""
        logger.info(f"Executing tool: {request.executable} with args {request.arguments}")
        
        start_time = time.time()
        try:
            # We enforce shell=False by default for security
            process = subprocess.run(
                [request.executable] + request.arguments,
                cwd=request.working_directory,
                capture_output=True,
                text=True,
                timeout=request.timeout_seconds,
                shell=False
            )
            duration = time.time() - start_time
            
            return ToolExecutionResult(
                stdout=process.stdout,
                stderr=process.stderr,
                exit_code=process.returncode,
                duration=duration,
                status="SUCCESS" if process.returncode == 0 else "ERROR"
            )
            
        except subprocess.TimeoutExpired as e:
            duration = time.time() - start_time
            logger.warning(f"Tool execution timed out after {duration}s: {request.executable}")
            # In python 3.13, e.stdout might be bytes or str depending on context, handle safely
            stdout = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else str(e.stdout or "")
            stderr = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else str(e.stderr or "")
            return ToolExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=-1,
                duration=duration,
                status="TIMEOUT"
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to execute {request.executable}: {e}")
            return ToolExecutionResult(
                stdout="",
                stderr=str(e),
                exit_code=-1,
                duration=duration,
                status="ERROR"
            )

tool_execution_service = ToolExecutionService()
