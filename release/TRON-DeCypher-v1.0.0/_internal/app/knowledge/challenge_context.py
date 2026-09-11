from dataclasses import dataclass, field


@dataclass
class ChallengeContext:
    category: str = "Misc"
    challenge_name: str = ""
    description: str = ""
    hints: list[str] = field(default_factory=list)
    custom_dictionary: list[str] = field(default_factory=list)
    flag_patterns: list[str] = field(default_factory=lambda: ["TRON{...}", "FLAG{...}", "CTF{...}"])
    enabled_transforms: list[str] = field(default_factory=list)

class ChallengeContextManager:
    def __init__(self) -> None:
        self.current_context = ChallengeContext()
        
    def set_context(self, category: str, flag_patterns: list[str] | None = None) -> None:
        self.current_context.category = category
        if flag_patterns:
            self.current_context.flag_patterns = flag_patterns

context_manager = ChallengeContextManager()
