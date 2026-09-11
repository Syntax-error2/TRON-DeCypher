import logging
import mimetypes
import uuid
from pathlib import Path

from app.models.artifact import Artifact
from app.services.case_service import case_service
from app.services.hashing_service import hashing_service
from app.services.storage_service import storage_service

logger = logging.getLogger(__name__)

class ArtifactService:
    """Service to manage artifact ingestion and metadata."""
    
    def ingest_file(self, case_id: str, source_path: str | Path) -> Artifact:
        """Ingests a single file into a case."""
        source = Path(source_path).resolve()
        
        # 1. Get case path to store evidence
        case_dir = case_service.get_case_path(case_id)
        evidence_dir = case_dir / "evidence"
        if not evidence_dir.exists():
            evidence_dir.mkdir(parents=True, exist_ok=True)
            
        # 2. Safely store the file
        original_filename = source.name
        stored_path = storage_service.store_artifact(evidence_dir, source, original_filename)
        
        # 3. Calculate metadata
        size = stored_path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(stored_path))
        mime_type = mime_type or "application/octet-stream"
        extension = stored_path.suffix.lower()
        
        # 4. Fingerprint
        hashes = hashing_service.hash_file(stored_path, ["md5", "sha256"])
        
        # 5. Create Artifact model
        artifact = Artifact(
            id=f"art_{uuid.uuid4().hex[:8]}",
            case_id=case_id,
            filename=original_filename,
            original_path=str(source),
            stored_path=str(stored_path),
            size=size,
            mime_type=mime_type,
            extension=extension,
            sha256=hashes.get("sha256"),
            md5=hashes.get("md5")
        )
        
        logger.info(f"Ingested artifact: {artifact.filename} ({artifact.id})")
        from app.database.database import db
        try:
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO artifacts (id, case_id, filename, original_path, stored_path, size, mime_type, extension, sha256, md5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (artifact.id, artifact.case_id, artifact.filename, artifact.original_path, artifact.stored_path, artifact.size, artifact.mime_type, artifact.extension, artifact.sha256, artifact.md5)
                )
        except Exception as e:
            logger.error(f"Failed to save artifact to DB: {e}")
        
        return artifact

    def ingest_multiple(self, case_id: str, source_paths: list[str | Path]) -> list[Artifact]:
        """Ingest multiple files into a case."""
        artifacts = []
        for path in source_paths:
            try:
                if Path(path).is_file():
                    artifacts.append(self.ingest_file(case_id, path))
            except Exception as e:
                logger.error(f"Failed to ingest {path}: {e}")
        return artifacts
        
    def ingest_directory(self, case_id: str, dir_path: str | Path) -> list[Artifact]:
        """Ingest all files in a directory recursively."""
        source_dir = Path(dir_path).resolve()
        artifacts = []
        for path in source_dir.rglob("*"):
            if path.is_file():
                try:
                    artifacts.append(self.ingest_file(case_id, path))
                except Exception as e:
                    logger.error(f"Failed to ingest {path}: {e}")
        return artifacts

    def get_all_artifacts(self, case_id: str) -> list[Artifact]:
        from app.database.database import db
        artifacts = []
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, case_id, filename, original_path, stored_path, size, mime_type, extension, sha256, md5 FROM artifacts WHERE case_id = ?", (case_id,))
                rows = cursor.fetchall()
                for r in rows:
                    artifacts.append(Artifact(
                        id=r["id"],
                        case_id=r["case_id"],
                        filename=r["filename"],
                        original_path=r["original_path"],
                        stored_path=r["stored_path"],
                        size=r["size"],
                        mime_type=r["mime_type"],
                        extension=r["extension"],
                        sha256=r["sha256"],
                        md5=r["md5"]
                    ))
        except Exception as e:
            logger.error(f"Failed to get artifacts: {e}")
        return artifacts

artifact_service = ArtifactService()

