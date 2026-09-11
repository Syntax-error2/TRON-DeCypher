from app.core.competition_service import competition_service
from app.database.database import db


def test_competition_timer() -> None:
    # Use a dummy case ID
    case_id = "test_comp_case"
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO cases (id, name) VALUES (?, ?)", (case_id, "Test Case"))
        conn.commit()
        
    competition_service.reset_timer(case_id)
    
    state = competition_service.get_timer_state(case_id)
    assert state["elapsed"] == 0
    assert not state["running"]
    
    competition_service.start_timer(case_id)
    state = competition_service.get_timer_state(case_id)
    assert state["running"]
    
    competition_service.pause_timer(case_id)
    state = competition_service.get_timer_state(case_id)
    assert not state["running"]
    assert state["elapsed"] >= 0
    
    competition_service.reset_timer(case_id)
    state = competition_service.get_timer_state(case_id)
    assert state["elapsed"] == 0
