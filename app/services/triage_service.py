import logging
from pathlib import Path
from typing import Any

from app.analyzers.core.entropy_analyzer import EntropyAnalyzer
from app.analyzers.core.file_identification import FileIdentificationAnalyzer
from app.analyzers.core.string_extractor import StringExtractorAnalyzer
from app.models.artifact import Artifact
from app.models.triage import TriageResult
from app.services.hashing_service import hashing_service

logger = logging.getLogger(__name__)

class TriageService:
    """Orchestrates basic artifact triage using core analyzers."""
    
    def __init__(self) -> None:
        self.file_id = FileIdentificationAnalyzer()
        self.string_ext = StringExtractorAnalyzer()
        self.entropy_calc = EntropyAnalyzer()
        
    def run_triage(self, artifact: Artifact) -> TriageResult:
        """Runs the standard triage pipeline on an artifact."""
        logger.info(f"Starting triage on {artifact.id}")
        
        result = TriageResult(artifact=artifact)
        
        path = artifact.stored_path
        context: dict[str, Any] = {}
        
        # 1. Hashing
        try:
            result.hashes = hashing_service.hash_file(Path(path))
        except Exception as e:
            logger.error(f"Hashing failed: {e}")
            
        # 2. File Identification
        try:
            if self.file_id.validate(path):
                result.file_identification = self.file_id.run(path, context)
        except Exception as e:
            logger.error(f"File identification failed: {e}")
            
        # 3. Strings
        try:
            if self.string_ext.validate(path):
                result.strings = self.string_ext.run(path, context)
        except Exception as e:
            logger.error(f"String extraction failed: {e}")
            
        # 4. Entropy
        try:
            if self.entropy_calc.validate(path):
                result.entropy = self.entropy_calc.run(path, context)
        except Exception as e:
            logger.error(f"Entropy calculation failed: {e}")
            
        # 5. Evaluate findings
        from app.services.finding_service import finding_service
        finding_service.evaluate_triage(result)
            
        result.execution_metadata["status"] = "COMPLETED"
        logger.info(f"Triage complete for {artifact.id}")
        
        return result

triage_service = TriageService()
