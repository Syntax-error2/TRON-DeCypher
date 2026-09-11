import time
from dataclasses import dataclass, field


@dataclass
class EvidenceBookmark:
    id: str
    case_id: str
    artifact_id: str
    bookmark_type: str # 'hex', 'string', 'ioc', 'packet', 'finding', 'decoder'
    location: str
    label: str
    description: str
    created_at: float = field(default_factory=time.time)

@dataclass
class CaseNote:
    id: str
    case_id: str
    title: str
    content: str
    category: str # General, Hypothesis, Finding, Flag, TODO, Observation
    linked_artifact: str = ""
    linked_finding: str = ""
    linked_ioc: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class CaseTask:
    id: str
    case_id: str
    title: str
    description: str
    priority: str # LOW, MEDIUM, HIGH, URGENT
    status: str # TODO, IN_PROGRESS, DONE
    linked_evidence: str = ""
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0.0

@dataclass
class CandidateFlag:
    id: str
    case_id: str
    artifact_id: str
    value: str
    source: str
    status: str # CANDIDATE, CONFIRMED, SUBMITTED, REJECTED
    notes: str = ""
    submitted: bool = False
    timestamp: float = field(default_factory=time.time)
    
@dataclass
class TimelineEvent:
    id: str
    case_id: str
    artifact_id: str
    event_type: str
    source: str
    summary: str
    timestamp: float = field(default_factory=time.time)
