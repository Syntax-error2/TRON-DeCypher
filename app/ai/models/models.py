from dataclasses import dataclass, field


@dataclass
class Recommendation:
    action: str
    reason: str
    evidence: str
    module: str
    confidence: str # Low, Medium, High

@dataclass
class AIAnalysisResponse:
    summary: str = ""
    observations: list[str] = field(default_factory=list)
    evidence_citations: list[str] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    confidence: str = "Unknown"
    warnings: list[str] = field(default_factory=list)

@dataclass
class AIMessage:
    role: str # 'user' or 'ai'
    content: str
    timestamp: float = 0.0

@dataclass
class AIContext:
    artifact_id: str = ""
    case_id: str = ""
    text_content: str = ""
    
@dataclass
class AIProviderConfig:
    provider: str = "Mock"
    model: str = "mock-model"
    base_url: str = ""
    api_key_configured: bool = False
    enabled: bool = False
    temperature: float = 0.2
    max_output_tokens: int = 4096
    request_timeout: int = 30
