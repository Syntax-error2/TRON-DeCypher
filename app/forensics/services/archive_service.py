import logging
import uuid
import zipfile
from pathlib import Path
from typing import Any

from app.models.artifact import Artifact
from app.services.hashing_service import hashing_service

logger = logging.getLogger(__name__)

class ArchiveService:
    """Safely inspects and extracts archives."""
    
    def is_safe_path(self, path: str) -> bool:
        """Checks for path traversal sequences and absolute paths."""
        if path.startswith(('/', '\\')):
            return False
        p = Path(path)
        return not (p.is_absolute() or ".." in p.parts)
        
    def inspect_zip(self, file_path: Path) -> list[dict[str, Any]]:
        """Lists contents of a ZIP safely."""
        contents: list[dict[str, Any]] = []
        if not zipfile.is_zipfile(file_path):
            return contents
            
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                for info in zf.infolist():
                    contents.append({
                        "filename": info.filename,
                        "size": info.file_size,
                        "compressed_size": info.compress_size,
                        "is_dir": info.is_dir(),
                        "safe": self.is_safe_path(info.filename)
                    })
        except Exception as e:
            logger.error(f"ZIP inspection failed: {e}")
            
        return contents
        
    def extract_zip(self, artifact: Artifact, cases_dir: Path) -> list[Artifact]:
        """Safely extracts all safe files from a ZIP into child artifacts."""
        extracted_artifacts: list[Artifact] = []
        source_path = Path(artifact.stored_path)
        
        if not zipfile.is_zipfile(source_path):
            return extracted_artifacts
            
        case_extracted_dir = cases_dir / artifact.case_id / "extracted"
        case_extracted_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with zipfile.ZipFile(source_path, 'r') as zf:
                for info in zf.infolist():
                    if info.is_dir() or not self.is_safe_path(info.filename):
                        continue
                        
                    new_id = f"art_{uuid.uuid4().hex[:12]}"
                    safe_filename = Path(info.filename).name # Flatten structure for extraction safety
                    target_path = case_extracted_dir / new_id
                    
                    with zf.open(info.filename) as src, open(target_path, "wb") as dst:
                        dst.write(src.read())
                        
                    hashes = hashing_service.hash_file(target_path)
                    
                    child_artifact = Artifact(
                        id=new_id,
                        case_id=artifact.case_id,
                        filename=safe_filename,
                        original_path=f"zip://{artifact.id}/{info.filename}",
                        stored_path=str(target_path.absolute()),
                        size=target_path.stat().st_size,
                        parent_artifact_id=artifact.id,
                        sha256=hashes.get("sha256"),
                        md5=hashes.get("md5"),
                    )
                    extracted_artifacts.append(child_artifact)
        except Exception as e:
            logger.error(f"Safe ZIP extraction failed: {e}")
            
        return extracted_artifacts

archive_service = ArchiveService()
