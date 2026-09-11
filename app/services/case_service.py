import logging
import uuid
from pathlib import Path

from app.core.config import settings
from app.models.case import Case

logger = logging.getLogger(__name__)

class CaseService:
    """Service to manage forensic cases and workspaces."""
    
    def __init__(self) -> None:
        self.cases_dir = Path(settings.cases_path)
        
    def create_case(self, name: str, description: str | None = None) -> Case:
        """Create a new case and its workspace directory."""
        case_id = f"case_{uuid.uuid4().hex[:8]}"
        case = Case(id=case_id, name=name, description=description)
        
        # Create workspace structure
        case_path = self.cases_dir / case_id
        for subdir in ["evidence", "decoded", "extracted", "screenshots", "reports", "exports"]:
            (case_path / subdir).mkdir(parents=True, exist_ok=True)
            
        # Save case.json
        self._save_case_json(case, case_path)
        
        logger.info(f"Created case workspace: {case_id} at {case_path}")
        return case
        
    def _save_case_json(self, case: Case, path: Path) -> None:
        case_file = path / "case.json"
        case_file.write_text(case.model_dump_json(indent=4), encoding="utf-8")
        
    def get_case(self, case_id: str) -> Case | None:
        # For now, we can read from db or case.json. 
        # Since Phase 1 uses DB, we'd query DB. But for simple file-based:
        case_file = self.cases_dir / case_id / "case.json"
        if case_file.exists():
            return Case.model_validate_json(case_file.read_text(encoding="utf-8"))
        return None
        
    def list_cases(self) -> list[Case]:
        cases = []
        if self.cases_dir.exists():
            for case_path in self.cases_dir.iterdir():
                if case_path.is_dir():
                    case_file = case_path / "case.json"
                    if case_file.exists():
                        cases.append(Case.model_validate_json(case_file.read_text(encoding="utf-8")))
        return cases
        
    def update_case(self, case: Case) -> None:
        case_path = self.get_case_path(case.id)
        if case_path.exists():
            self._save_case_json(case, case_path)
        
    def get_case_path(self, case_id: str) -> Path:
        """Get the root path of a case workspace."""
        return self.cases_dir / case_id

case_service = CaseService()
