import logging
import time
from typing import Any

from app.database.database import db

logger = logging.getLogger(__name__)

class CompetitionService:
    """Manages the competition timer and state per case."""
    
    def get_timer_state(self, case_id: str) -> dict[str, Any]:
        """Returns elapsed time, running status, etc."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timer_elapsed, timer_state, timer_start_ts FROM cases WHERE id = ?", (case_id,))
            row = cursor.fetchone()
            
            if not row:
                return {"elapsed": 0, "running": False}
                
            elapsed = row['timer_elapsed'] or 0.0
            state = row['timer_state'] or 'stopped'
            start_ts = row['timer_start_ts'] or 0.0
            
            if state == 'running' and start_ts > 0:
                elapsed += (time.time() - start_ts)
                
            return {"elapsed": elapsed, "running": (state == 'running')}
            
    def start_timer(self, case_id: str) -> None:
        state = self.get_timer_state(case_id)
        if state["running"]:
            return # already running
            
        now = time.time()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cases SET timer_state = 'running', timer_start_ts = ? WHERE id = ?",
                (now, case_id)
            )
            conn.commit()
            
    def pause_timer(self, case_id: str) -> None:
        state = self.get_timer_state(case_id)
        if not state["running"]:
            return
            
        elapsed = state["elapsed"]
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cases SET timer_state = 'stopped', timer_elapsed = ?, timer_start_ts = 0 WHERE id = ?",
                (elapsed, case_id)
            )
            conn.commit()
            
    def reset_timer(self, case_id: str) -> None:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE cases SET timer_state = 'stopped', timer_elapsed = 0, timer_start_ts = 0 WHERE id = ?",
                (case_id,)
            )
            conn.commit()
            
    def get_dashboard_metrics(self, case_id: str) -> dict[str, int]:
        """Gathers fast counts for the Competition Dashboard."""
        metrics = {
            "artifacts": 0,
            "findings": 0,
            "iocs": 0,
            "flags": 0,
            "tasks": 0,
            "notes": 0
        }
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM artifacts WHERE case_id = ?", (case_id,))
            metrics["artifacts"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM findings WHERE case_id = ?", (case_id,))
            metrics["findings"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM iocs WHERE case_id = ?", (case_id,))
            metrics["iocs"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM flags WHERE case_id = ?", (case_id,))
            metrics["flags"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM case_tasks WHERE case_id = ?", (case_id,))
            metrics["tasks"] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM case_notes WHERE case_id = ?", (case_id,))
            metrics["notes"] = cursor.fetchone()[0]
            
        return metrics

competition_service = CompetitionService()
