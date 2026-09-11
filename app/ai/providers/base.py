from abc import ABC, abstractmethod

from app.ai.models.models import AIAnalysisResponse, AIProviderConfig


class AIProvider(ABC):
    def __init__(self, config: AIProviderConfig):
        self.config = config
        
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def is_configured(self) -> bool:
        pass
        
    @abstractmethod
    def analyze(self, system_prompt: str, user_prompt: str) -> AIAnalysisResponse:
        pass
