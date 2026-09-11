import logging
import uuid
from pathlib import Path

from app.models.artifact import Artifact
from app.services.hashing_service import hashing_service

logger = logging.getLogger(__name__)

class CarvingService:
    """Safely extracts blocks of data into new Artifacts."""
    
    def extract_appended_data(self, artifact: Artifact, offset: int, cases_dir: Path) -> Artifact:
        """Extracts data from an offset to EOF and registers it as a new child artifact."""
        source_path = Path(artifact.stored_path)
        if not source_path.exists():
            raise FileNotFoundError("Source artifact missing")
            
        case_extracted_dir = cases_dir / artifact.case_id / "extracted"
        case_extracted_dir.mkdir(parents=True, exist_ok=True)
        
        new_id = f"art_{uuid.uuid4().hex[:12]}"
        new_filename = f"extracted_{artifact.filename}_0x{offset:X}.bin"
        target_path = case_extracted_dir / new_id
        
        try:
            with open(source_path, "rb") as src, open(target_path, "wb") as dst:
                src.seek(offset)
                while True:
                    chunk = src.read(8192)
                    if not chunk:
                        break
                    dst.write(chunk)
                    
            hashes = hashing_service.hash_file(target_path)
            
            child_artifact = Artifact(
                id=new_id,
                case_id=artifact.case_id,
                filename=new_filename,
                original_path=f"carved://{artifact.id}@{offset}",
                stored_path=str(target_path.absolute()),
                size=target_path.stat().st_size,
                parent_artifact_id=artifact.id,
                sha256=hashes.get("sha256"),
                md5=hashes.get("md5"),
            )
            return child_artifact
            
        except Exception as e:
            if target_path.exists():
                target_path.unlink()
            logger.error(f"Failed to carve appended data: {e}")
            raise

carving_service = CarvingService()
