from typing import Any

from app.memory.models import (
    MemoryAnalysisResult,
    MemoryModule,
    MemoryNetworkConnection,
    MemoryProcess,
)


class VolatilityParser:
    """Parses Volatility 3 structured JSON output."""
    
    def parse_pslist(self, data: list[dict[str, Any]], result: MemoryAnalysisResult) -> None:
        if not data: return
        for item in data:
            try:
                pid = int(item.get("PID", 0))
                ppid = int(item.get("PPID", 0))
                name = str(item.get("ImageFileName", "Unknown"))
                start = str(item.get("CreateTime", ""))
                
                result.processes.append(MemoryProcess(
                    pid=pid,
                    ppid=ppid,
                    name=name,
                    start_time=start
                ))
            except Exception:
                pass
                
    def parse_netscan(self, data: list[dict[str, Any]], result: MemoryAnalysisResult) -> None:
        if not data: return
        for item in data:
            try:
                pid = int(item.get("PID", 0))
                owner = str(item.get("Owner", "Unknown"))
                proto = str(item.get("Protocol", "TCP"))
                local_addr = str(item.get("LocalAddr", ""))
                local_port = int(item.get("LocalPort", 0))
                foreign_addr = str(item.get("ForeignAddr", ""))
                foreign_port = int(item.get("ForeignPort", 0))
                state = str(item.get("State", ""))
                
                if local_addr and foreign_addr:
                    result.connections.append(MemoryNetworkConnection(
                        process_name=owner,
                        pid=pid,
                        source_ip=local_addr,
                        source_port=local_port,
                        dest_ip=foreign_addr,
                        dest_port=foreign_port,
                        state=state,
                        protocol=proto
                    ))
            except Exception:
                pass
                
    def parse_dlllist(self, data: list[dict[str, Any]], result: MemoryAnalysisResult) -> None:
        if not data: return
        for item in data:
            try:
                pid = int(item.get("PID", 0))
                name = str(item.get("Name", "Unknown"))
                path = str(item.get("Path", ""))
                base = str(item.get("Base", ""))
                size = str(item.get("Size", ""))
                
                result.modules.append(MemoryModule(
                    process_name="Unknown", # Will be correlated later
                    pid=pid,
                    name=name,
                    path=path,
                    base_address=base,
                    size=size
                ))
            except Exception:
                pass

volatility_parser = VolatilityParser()
