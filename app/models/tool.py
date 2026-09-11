import time

from pydantic import BaseModel, Field


class Tool(BaseModel):
    id: str
    name: str
    executable: str
    tool_type: str = "EXTERNAL EXECUTABLE"  # BUILT-IN, PYTHON PACKAGE, EXTERNAL EXECUTABLE
    status: str = "NOT_INSTALLED"          # AVAILABLE, PYTHON_AVAILABLE, CONFIGURED, NOT_INSTALLED, NOT_ON_PATH, INVALID, VERSION_UNKNOWN, ERROR
    path: str | None = None
    configured_path: str | None = None
    version: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    detection_method: str = "shutil.which"
    last_checked: float = Field(default_factory=time.time)
