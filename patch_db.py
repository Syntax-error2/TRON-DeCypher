import re

with open('app/database/database.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add knowledge tables before conn.commit()
new_tables = '''            # CTF Knowledge Tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    filename TEXT,
                    sha256 TEXT,
                    page_count INTEGER,
                    source_type TEXT,
                    imported_at REAL,
                    extraction_status TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_sections (
                    id TEXT PRIMARY KEY,
                    document_id TEXT,
                    page INTEGER,
                    section TEXT,
                    category TEXT,
                    content TEXT,
                    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE,
                    document_id TEXT,
                    section_id TEXT,
                    topic TEXT,
                    text TEXT,
                    keywords TEXT,
                    tool_names TEXT,
                    command_names TEXT,
                    techniques TEXT,
                    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id),
                    FOREIGN KEY (section_id) REFERENCES knowledge_sections(id)
                )
            """)
            
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts USING fts5(
                    topic,
                    text,
                    keywords,
                    tool_names,
                    command_names,
                    techniques,
                    content='knowledge_chunks',
                    content_rowid='id'
                )
            """)
            
            # Triggers to keep FTS5 synchronized
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_chunks_ai AFTER INSERT ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(rowid, topic, text, keywords, tool_names, command_names, techniques)
                    VALUES (new.id, new.topic, new.text, new.keywords, new.tool_names, new.command_names, new.techniques);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_chunks_ad AFTER DELETE ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts, rowid, topic, text, keywords, tool_names, command_names, techniques)
                    VALUES ('delete', old.id, old.topic, old.text, old.keywords, old.tool_names, old.command_names, old.techniques);
                END;
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS knowledge_chunks_au AFTER UPDATE ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts, rowid, topic, text, keywords, tool_names, command_names, techniques)
                    VALUES ('delete', old.id, old.topic, old.text, old.keywords, old.tool_names, old.command_names, old.techniques);
                    INSERT INTO knowledge_chunks_fts(rowid, topic, text, keywords, tool_names, command_names, techniques)
                    VALUES (new.id, new.topic, new.text, new.keywords, new.tool_names, new.command_names, new.techniques);
                END;
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_topics (
                    id TEXT PRIMARY KEY,
                    topic TEXT,
                    category TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_tools (
                    id TEXT PRIMARY KEY,
                    tool TEXT,
                    category TEXT,
                    purpose TEXT,
                    source TEXT,
                    page INTEGER,
                    reference_command TEXT,
                    notes TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_commands (
                    id TEXT PRIMARY KEY,
                    tool TEXT,
                    command TEXT,
                    purpose TEXT,
                    category TEXT,
                    source TEXT,
                    page INTEGER,
                    risk_level TEXT,
                    requires_explicit_execution INTEGER DEFAULT 1
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_workflows (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    title TEXT,
                    steps TEXT,
                    source TEXT
                )
            """)
            
            conn.commit()'''

content = content.replace("            conn.commit()", new_tables, 1)

with open('app/database/database.py', 'w', encoding='utf-8') as f:
    f.write(content)

