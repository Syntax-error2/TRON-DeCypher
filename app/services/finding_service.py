import logging
import uuid
from typing import Any

from app.models.finding import Finding
from app.models.triage import TriageResult

logger = logging.getLogger(__name__)

class FindingService:
    """Manages the creation and tracking of findings from analyzers."""
    
    VALID_SEVERITIES = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def create_finding(
        self,
        case_id: str,
        category: str,
        severity: str,
        title: str,
        description: str,
        artifact_id: str | None = None,
        evidence: Any | None = None
    ) -> Finding:
        """Creates a normalized finding."""
        if severity not in self.VALID_SEVERITIES:
            logger.warning(f"Invalid severity '{severity}' normalized to 'INFO'")
            severity = "INFO"
            
        finding = Finding(
            id=f"fnd_{uuid.uuid4().hex[:8]}",
            case_id=case_id,
            artifact_id=artifact_id,
            category=category,
            severity=severity,
            title=title,
            description=description,
            evidence=evidence
        )
        
        logger.info(f"Created finding: [{severity}] {title}")
        return finding
        
    def evaluate_triage(self, triage: TriageResult) -> None:
        """Generates simple findings from triage without making definitive conclusions."""
        # Example: high entropy finding
        if triage.entropy and triage.entropy.entropy > 7.9:
            finding = self.create_finding(
                case_id=triage.artifact.case_id,
                artifact_id=triage.artifact.id,
                category="metadata",
                severity="INFO",
                title="High Entropy Detected",
                description="The file exhibits very high entropy, which may indicate packing, compression, or encryption.",
                evidence={"entropy": triage.entropy.entropy}
            )
            triage.findings.append(finding)
            
        # Example: Executable file identified
        if "executable" in str(triage.file_identification.get("mime_type_os", "")).lower():
            finding = self.create_finding(
                case_id=triage.artifact.case_id,
                artifact_id=triage.artifact.id,
                category="metadata",
                severity="INFO",
                title="Executable File Type",
                description="The artifact appears to be an executable file.",
                evidence={"mime": triage.file_identification.get("mime_type_os")}
            )
            triage.findings.append(finding)

finding_service = FindingService()
