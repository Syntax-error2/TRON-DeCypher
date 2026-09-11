from typing import Any

from app.database.database import DatabaseManager


def test_database_initialization(tmp_path: Any) -> None:
    db_file = tmp_path / "test.sqlite"
    db = DatabaseManager(db_path=str(db_file))
    
    db.initialize()
    
    assert db_file.exists()
    
    # Verify tables
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cursor.fetchall()]
        
        assert "cases" in tables
        assert "artifacts" in tables
        assert "findings" in tables
        assert "results" in tables
        assert "tools" in tables
        assert "analysis_jobs" in tables
