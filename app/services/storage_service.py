import logging
import os
import re
import shutil
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageService:
    """Safely stores imported artifacts into case workspaces."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal and invalid characters."""
        # Strip path info just in case
        filename = Path(filename).name
        # Remove anything that isn't alphanumeric, dash, dot, or underscore
        clean_name = re.sub(r'[^a-zA-Z0-9.\-_]', '_', filename)
        if not clean_name or clean_name == '.' or clean_name == '..':
            clean_name = f"unnamed_file_{uuid.uuid4().hex[:8]}"
        return clean_name
        
    def store_artifact(self, case_evidence_dir: Path, source_path: str | Path, original_filename: str) -> Path:
        """
        Safely copies a file into the case evidence directory.
        Returns the new stored Path.
        """
        source = Path(source_path).resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Source file not found: {source}")
            
        sanitized = self.sanitize_filename(original_filename)
        # Prevent overwriting by appending a short UUID
        unique_id = uuid.uuid4().hex[:6]
        name, ext = os.path.splitext(sanitized)
        stored_filename = f"{name}_{unique_id}{ext}"
        
        destination = (case_evidence_dir / stored_filename).resolve()
        
        # Ensure destination is strictly inside case_evidence_dir (path traversal protection)
        if not str(destination).startswith(str(case_evidence_dir.resolve())):
            raise ValueError("Path traversal attempt detected during storage.")
            
        # Copy the file
        logger.info(f"Storing artifact {source} -> {destination}")
        shutil.copy2(source, destination)
        
        return destination

storage_service = StorageService()
