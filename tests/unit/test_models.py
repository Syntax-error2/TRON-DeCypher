from app.models.case import Case


def test_case_model() -> None:
    case = Case(id="case_123", name="Test Case")
    assert case.id == "case_123"
    assert case.name == "Test Case"
    assert case.status == "open"
