import logging
from dataclasses import dataclass
from typing import Any

from app.database.database import db

logger = logging.getLogger(__name__)

@dataclass
class ReportConfig:
    case_id: str
    export_path: str
    format_type: str # 'json', 'csv', 'pdf'
    include_artifacts: bool = True
    include_findings: bool = True
    include_iocs: bool = True
    include_timeline: bool = True
    mask_sensitive_data: bool = True

class ReportingService:
    """Consolidates evidence and dispatches to appropriate exporters."""
    
    def generate_report(self, config: ReportConfig) -> bool:
        logger.info(f"Generating {config.format_type} report for case {config.case_id} at {config.export_path}")
        
        # 1. Gather Data
        data: dict[str, Any] = self._gather_case_data(config)
        
        # 2. Mask Sensitive Data
        if config.mask_sensitive_data:
            data = self._mask_data(data)
            
        # 3. Export
        try:
            if config.format_type == 'json':
                from app.reporting.exporters.json_exporter import export_json
                export_json(data, config.export_path)
            elif config.format_type == 'csv':
                from app.reporting.exporters.csv_exporter import export_csv
                export_csv(data, config.export_path)
            elif config.format_type == 'pdf':
                from app.reporting.exporters.pdf_exporter import export_pdf
                export_pdf(data, config.export_path)
            else:
                logger.error(f"Unknown format type {config.format_type}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return False
            
    def _gather_case_data(self, config: ReportConfig) -> dict[str, Any]:
        data: dict[str, Any] = {"schema_version": "1.0", "case": {}, "artifacts": [], "findings": [], "iocs": [], "timeline": []}
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Case Data
            cursor.execute("SELECT * FROM cases WHERE id = ?", (config.case_id,))
            case_row = cursor.fetchone()
            if case_row:
                data["case"] = dict(case_row)
                
            if config.include_artifacts:
                cursor.execute("SELECT * FROM artifacts WHERE case_id = ?", (config.case_id,))
                data["artifacts"] = [dict(r) for r in cursor.fetchall()]
                
            if config.include_findings:
                cursor.execute("SELECT * FROM findings WHERE case_id = ?", (config.case_id,))
                data["findings"] = [dict(r) for r in cursor.fetchall()]
                
            if config.include_iocs:
                cursor.execute("SELECT * FROM iocs WHERE case_id = ?", (config.case_id,))
                data["iocs"] = [dict(r) for r in cursor.fetchall()]
                
            if config.include_timeline:
                cursor.execute("SELECT * FROM timeline_events WHERE case_id = ?", (config.case_id,))
                data["timeline"] = [dict(r) for r in cursor.fetchall()]
                
        return data
        
    def _mask_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Uses the AI Data Redactor to scrub strings before export."""
        # Simple recursive string redactor using the existing redactor
        from app.ai.safety.redactor import ai_redactor
        
        def _recursive_mask(obj: Any) -> Any:
            if isinstance(obj, str):
                return ai_redactor.redact(obj)
            elif isinstance(obj, dict):
                return {k: _recursive_mask(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [_recursive_mask(x) for x in obj]
            return obj
            
        from typing import cast; return cast(dict[str, Any], _recursive_mask(data))

reporting_service = ReportingService()
