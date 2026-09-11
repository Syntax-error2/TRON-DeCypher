from app.ai.models.models import AIContext
from app.ai.safety.redactor import ai_redactor
from app.database.database import db


class AIContextBuilder:
    MAX_CHARS = 50000
    
    def build_artifact_context(self, artifact_id: str) -> AIContext:
        context = AIContext(artifact_id=artifact_id)
        lines = []
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Artifact
            cursor.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,))
            art = cursor.fetchone()
            if not art:
                context.text_content = "Artifact not found."
                return context
                
            lines.append("--- ARTIFACT METADATA ---")
            lines.append(f"Name: {art['filename']}")
            lines.append(f"Type: {art['mime_type']}")
            lines.append(f"Size: {art['size']} bytes")
            lines.append(f"SHA256: {art['sha256']}")
            
            # Findings
            cursor.execute("SELECT * FROM findings WHERE artifact_id = ?", (artifact_id,))
            findings = cursor.fetchall()
            if findings:
                lines.append("\n--- FINDINGS ---")
                for f in findings:
                    lines.append(f"[{f['severity']}] {f['title']}: {f['description']}")
                    
            # IOCs
            cursor.execute("SELECT * FROM iocs WHERE artifact_id = ?", (artifact_id,))
            iocs = cursor.fetchall()
            if iocs:
                lines.append("\n--- IOCs ---")
                for ioc in iocs[:50]:
                    lines.append(f"{ioc['ioc_type']}: {ioc['value']}")
                if len(iocs) > 50:
                    lines.append(f"... and {len(iocs) - 50} more")
                    
        raw_context = "\n".join(lines)
        if len(raw_context) > self.MAX_CHARS:
            raw_context = raw_context[:self.MAX_CHARS] + "\n[CONTEXT TRUNCATED DUE TO SIZE]"
            
        context.text_content = ai_redactor.redact(raw_context)
        return context

ai_context_builder = AIContextBuilder()
