import re


class AIDataRedactor:
    JWT_REGEX = re.compile(r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")
    BEARER_REGEX = re.compile(r"(?i)(bearer|token|api[_-]?key)[\s:=]+([a-zA-Z0-9_\-\.]{20,})")
    PASSWORD_REGEX = re.compile(r"(?i)(password|passwd|pwd)[\s:=]+([^\s]+)")
    
    def redact(self, content: str) -> str:
        if not content:
            return ""
            
        redacted = content
        redacted = self.JWT_REGEX.sub("[REDACTED_JWT]", redacted)
        
        def bearer_replacer(match: re.Match[str]) -> str:
            return f"{match.group(1)} [REDACTED_TOKEN]"
            
        redacted = self.BEARER_REGEX.sub(bearer_replacer, redacted)
        
        def pwd_replacer(match: re.Match[str]) -> str:
            return f"{match.group(1)} [REDACTED_PASSWORD]"
            
        redacted = self.PASSWORD_REGEX.sub(pwd_replacer, redacted)
        
        return redacted

ai_redactor = AIDataRedactor()
