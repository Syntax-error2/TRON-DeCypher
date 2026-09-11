from app.ai.models.models import AIAnalysisResponse, Recommendation
from app.ai.providers.base import AIProvider


class MockAIProvider(AIProvider):
    def name(self) -> str:
        return "Mock Provider"
        
    def is_configured(self) -> bool:
        return True
        
    def analyze(self, system_prompt: str, user_prompt: str) -> AIAnalysisResponse:
        return AIAnalysisResponse(
            summary="This is a mock AI response.",
            observations=["Observation 1 (Mock)", "Observation 2 (Mock)"],
            evidence_citations=["Evidence Mock A"],
            recommendations=[
                Recommendation(
                    action="Run Strings Analysis",
                    reason="Mock reason to check strings.",
                    evidence="Mock evidence",
                    module="Binary",
                    confidence="High"
                )
            ],
            confidence="High"
        )
