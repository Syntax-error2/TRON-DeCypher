import re

with open('app/knowledge/knowledge_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
    def _sanitize_fts_query(self, query: str) -> str:
        # Remove punctuation that breaks FTS5 MATCH
        safe = re.sub(r'[^a-zA-Z0-9 ]', ' ', query)
        # Split into words and join with OR for better matching
        words = [w for w in safe.split() if len(w) > 2]
        if not words: return safe
        return " OR ".join(words)

    def search(self, query: str) -> List[Dict[str, Any]]:
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
            
    def search_category(self, category: str, query: str = "") -> List[Dict[str, Any]]:
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
'''
# I'll just rewrite knowledge_service.py by doing a replace.
import re
content = re.sub(r'    def search\(self.*?def search_category\(self.*?\n.*?return \[dict\(r\) for r in rows\]', patch.strip(), content, flags=re.DOTALL)

with open('app/knowledge/knowledge_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
