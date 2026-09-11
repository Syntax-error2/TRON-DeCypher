import re
import time
import uuid
from typing import Any

from app.database.database import db


class CTFKnowledgeService:
    def _sanitize_fts_query(self, query: str) -> str:
        # Remove punctuation that breaks FTS5 MATCH
        safe = re.sub(r'[^a-zA-Z0-9 ]', ' ', query)
        # Split into words and join with OR for better matching
        words = [w for w in safe.split() if len(w) > 2]
        if not words: return safe
        return " OR ".join(words)

    def search(self, query: str) -> list[dict[str, Any]]:
        safe_query = self._sanitize_fts_query(query)
        if not safe_query.strip():
            return []
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.topic, c.text, c.keywords, c.tool_names, c.command_names, 
                       d.title as source, s.page, s.section, s.category, d.source_type
                FROM knowledge_chunks_fts f
                JOIN knowledge_chunks c ON f.rowid = c.id
                JOIN knowledge_sections s ON c.section_id = s.id
                JOIN knowledge_documents d ON c.document_id = d.id
                WHERE knowledge_chunks_fts MATCH ?
                ORDER BY rank
                LIMIT 50
            """, (safe_query,))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
            
    def search_category(self, category: str, query: str = "") -> list[dict[str, Any]]:
        safe_query = self._sanitize_fts_query(query) if query else ""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if safe_query:
                cursor.execute("""
                    SELECT c.topic, c.text, c.keywords, d.title as source, s.page, s.section, s.category, d.source_type
                    FROM knowledge_chunks_fts f
                    JOIN knowledge_chunks c ON f.rowid = c.id
                    JOIN knowledge_sections s ON c.section_id = s.id
                    JOIN knowledge_documents d ON c.document_id = d.id
                    WHERE knowledge_chunks_fts MATCH ? AND s.category = ?
                    ORDER BY rank
                    LIMIT 50
                """, (safe_query, category))

    def search_tool(self, tool: str) -> list[dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tool, category, purpose, source, page, reference_command, notes
                FROM knowledge_tools
                WHERE tool LIKE ?
            ''', (f'%{tool}%',))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
            
    def search_command(self, query: str) -> list[dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tool, command, purpose, category, source, page, risk_level, requires_explicit_execution
                FROM knowledge_commands
                WHERE tool LIKE ? OR command LIKE ? OR purpose LIKE ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def get_workflow(self, category: str) -> list[dict[str, Any]]:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, title, steps, source
                FROM knowledge_workflows
                WHERE category = ? OR category LIKE ?
            ''', (category, f'%{category}%'))
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
            
    def register_document(self, title: str, filename: str, sha256: str, source_type: str, page_count: int = 1) -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # Deduplication
            cursor.execute('SELECT id FROM knowledge_documents WHERE sha256 = ?', (sha256,))
            row = cursor.fetchone()
            if row:
                return row['id']
                
            doc_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO knowledge_documents (id, title, filename, sha256, page_count, source_type, imported_at, extraction_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (doc_id, title, filename, sha256, page_count, source_type, time.time(), "COMPLETED"))
            conn.commit()
            return doc_id
            
    def add_section(self, document_id: str, page: int, section: str, category: str, content: str) -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            sec_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO knowledge_sections (id, document_id, page, section, category, content)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (sec_id, document_id, page, section, category, content))
            conn.commit()
            return sec_id
            
    def add_chunk(self, document_id: str, section_id: str, topic: str, text: str, keywords: str, tool_names: str, command_names: str, techniques: str) -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            chunk_uuid = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO knowledge_chunks (uuid, document_id, section_id, topic, text, keywords, tool_names, command_names, techniques)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (chunk_uuid, document_id, section_id, topic, text, keywords, tool_names, command_names, techniques))
            conn.commit()
            return chunk_uuid
            
    def add_tool(self, tool: str, category: str, purpose: str, source: str, page: int, reference_command: str = "", notes: str = "") -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            tool_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO knowledge_tools (id, tool, category, purpose, source, page, reference_command, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tool_id, tool, category, purpose, source, page, reference_command, notes))
            conn.commit()
            return tool_id
            
    def add_command(self, tool: str, command: str, purpose: str, category: str, source: str, page: int, risk_level: str = "HIGH") -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cmd_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO knowledge_commands (id, tool, command, purpose, category, source, page, risk_level, requires_explicit_execution)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cmd_id, tool, command, purpose, category, source, page, risk_level, 1))
            conn.commit()
            return cmd_id
            
    def add_workflow(self, category: str, title: str, steps: str, source: str) -> str:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            wf_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO knowledge_workflows (id, category, title, steps, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (wf_id, category, title, steps, source))
            conn.commit()
            return wf_id

knowledge_service = CTFKnowledgeService()

