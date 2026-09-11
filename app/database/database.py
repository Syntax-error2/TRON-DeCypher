import logging
import sqlite3

from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str | None = None):
        if db_path:
            path = db_path.replace("sqlite:///", "")
            self.db_path = path
        else:
            self.db_path = settings.database_url.replace("sqlite:///", "")

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        """Create tables if they do not exist."""
        logger.info(f"Initializing database at {self.db_path}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'open',
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    original_path TEXT,
                    stored_path TEXT,
                    size INTEGER,
                    mime_type TEXT,
                    extension TEXT,
                    sha256 TEXT,
                    md5 TEXT,
                    parent_artifact_id TEXT,
                    created_at TIMESTAMP,
                    modified_at TIMESTAMP,
                    imported_at TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases (id),
                    FOREIGN KEY (parent_artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            # Migration logic for parent_artifact_id
            cursor.execute("PRAGMA table_info(artifacts)")
            columns = [col[1] for col in cursor.fetchall()]
            if "parent_artifact_id" not in columns:
                cursor.execute("ALTER TABLE artifacts ADD COLUMN parent_artifact_id TEXT REFERENCES artifacts(id)")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    artifact_id TEXT,
                    category TEXT,
                    severity TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    evidence TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases (id),
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id TEXT PRIMARY KEY,
                    analyzer TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    status TEXT,
                    output TEXT,
                    created_at TIMESTAMP,
                    execution_time REAL,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    executable TEXT NOT NULL,
                    version TEXT,
                    path TEXT,
                    available BOOLEAN
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_jobs (
                    id TEXT PRIMARY KEY,
                    analyzer_name TEXT NOT NULL,
                    artifact_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    status TEXT DEFAULT 'PENDING',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    duration REAL,
                    result TEXT,
                    error TEXT,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id),
                    FOREIGN KEY (case_id) REFERENCES cases (id)
                )
            """)
            
            # Phase 5: IOCs and Intelligence
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iocs (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    ioc_type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    normalized_value TEXT NOT NULL,
                    first_seen TIMESTAMP,
                    last_seen TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ioc_occurrences (
                    id TEXT PRIMARY KEY,
                    ioc_id TEXT NOT NULL,
                    source_artifact_id TEXT,
                    source_result_id TEXT,
                    source_location TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (ioc_id) REFERENCES iocs (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS intel_results (
                    id TEXT PRIMARY KEY,
                    ioc_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    response_summary TEXT,
                    retrieved_at TIMESTAMP,
                    expiry TIMESTAMP,
                    FOREIGN KEY (ioc_id) REFERENCES iocs (id)
                )
            """)
            
            # Phase 6: Network Forensics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pcap_captures (
                    artifact_id TEXT PRIMARY KEY,
                    packet_count INTEGER,
                    duration REAL,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_flows (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL,
                    src_ip TEXT,
                    dst_ip TEXT,
                    src_port INTEGER,
                    dst_port INTEGER,
                    protocol TEXT,
                    packet_count INTEGER,
                    bytes_transferred INTEGER,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS network_events (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    summary TEXT,
                    details TEXT,
                    timestamp TIMESTAMP,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts (id)
                )
            """)
            
            # Phase 7: Crypto History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crypto_history (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    input_text TEXT,
                    algorithm TEXT,
                    operation TEXT,
                    result_text TEXT,
                    parameters TEXT,
                    timestamp REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            # Phase 8: Web History
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS web_history (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    method TEXT,
                    url TEXT,
                    status_code INTEGER,
                    duration REAL,
                    request_blob TEXT,
                    response_blob TEXT,
                    timestamp REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            # Phase 9: Binary Analysis Runs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS binary_analysis_runs (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT,
                    format TEXT,
                    architecture TEXT,
                    timestamp REAL,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
                )
            ''')
            
            # Phase 10: Memory Analysis Runs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_analysis_runs (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT,
                    os_hint TEXT,
                    process_count INTEGER,
                    timestamp REAL,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
                )
            ''')
            
            # Phase 11: Malware Triage Runs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS malware_triage_runs (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT,
                    triage_score INTEGER,
                    classification TEXT,
                    timestamp REAL,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
                )
            ''')
            
            # Phase 11: YARA Matches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS yara_matches (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT,
                    rule_name TEXT,
                    timestamp REAL,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
                )
            ''')
            
            # Phase 12: AI Copilot
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    timestamp REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_messages (
                    id TEXT PRIMARY KEY,
                    artifact_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp REAL,
                    FOREIGN KEY (artifact_id) REFERENCES artifacts(id)
                )
            ''')
            
                        # Phase 13: Alter cases
            try:
                cursor.execute("ALTER TABLE cases ADD COLUMN challenge_name TEXT")
                cursor.execute("ALTER TABLE cases ADD COLUMN challenge_category TEXT")
                cursor.execute("ALTER TABLE cases ADD COLUMN author TEXT")
                cursor.execute("ALTER TABLE cases ADD COLUMN priority TEXT")
                cursor.execute("ALTER TABLE cases ADD COLUMN start_time REAL")
                cursor.execute("ALTER TABLE cases ADD COLUMN end_time REAL")
                cursor.execute("ALTER TABLE cases ADD COLUMN objective TEXT")
                cursor.execute("ALTER TABLE cases ADD COLUMN timer_elapsed REAL DEFAULT 0")
                cursor.execute("ALTER TABLE cases ADD COLUMN timer_state TEXT DEFAULT 'stopped'")
                cursor.execute("ALTER TABLE cases ADD COLUMN timer_start_ts REAL")
            except sqlite3.OperationalError:
                # Columns already exist
                pass
                
            # Phase 13: Workspace Tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS case_notes (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    title TEXT,
                    content TEXT,
                    category TEXT,
                    linked_artifact TEXT,
                    linked_finding TEXT,
                    linked_ioc TEXT,
                    timestamp REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS case_tasks (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    title TEXT,
                    description TEXT,
                    priority TEXT,
                    status TEXT,
                    linked_evidence TEXT,
                    created_at REAL,
                    completed_at REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    artifact_id TEXT,
                    bookmark_type TEXT,
                    location TEXT,
                    label TEXT,
                    description TEXT,
                    created_at REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flags (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    artifact_id TEXT,
                    value TEXT,
                    source TEXT,
                    status TEXT,
                    submitted INTEGER,
                    notes TEXT,
                    timestamp REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timeline_events (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    artifact_id TEXT,
                    event_type TEXT,
                    source TEXT,
                    summary TEXT,
                    timestamp REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    case_id TEXT,
                    name TEXT,
                    path TEXT,
                    type TEXT,
                    created_at REAL,
                    FOREIGN KEY (case_id) REFERENCES cases(id)
                )
            ''')
            # Indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_case_id ON artifacts (case_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_findings_case_id ON findings (case_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_jobs_case_id ON analysis_jobs (case_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_jobs_artifact_id ON analysis_jobs (artifact_id)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_iocs_case_id ON iocs (case_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_iocs_normalized ON iocs (normalized_value)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ioc_occurrences_ioc_id ON ioc_occurrences (ioc_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_intel_results_ioc_id ON intel_results (ioc_id)")
            
            # CTF Knowledge Tables
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
            
            conn.commit()
        logger.info("Database initialization complete.")

db = DatabaseManager()
