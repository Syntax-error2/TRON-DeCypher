from app.ai.models.models import AIAnalysisResponse, AIProviderConfig
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.safety.redactor import ai_redactor


def test_ai_redactor() -> None:
    content = "Here is a secret bearer token: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c "
    redacted = ai_redactor.redact(content)
    assert "eyJhbGci" not in redacted
    assert "[REDACTED_JWT]" in redacted
    
    content2 = "password: SuperSecret123!"
    redacted2 = ai_redactor.redact(content2)
    assert "SuperSecret123!" not in redacted2
    assert "[REDACTED_PASSWORD]" in redacted2
    
def test_mock_provider() -> None:
    config = AIProviderConfig()
    provider = MockAIProvider(config)
    
    assert provider.name() == "Mock Provider"
    assert provider.is_configured()
    
    resp = provider.analyze("system", "user")
    assert isinstance(resp, AIAnalysisResponse)
    assert resp.summary == "This is a mock AI response."
    assert len(resp.recommendations) == 1
    assert resp.recommendations[0].action == "Run Strings Analysis"
