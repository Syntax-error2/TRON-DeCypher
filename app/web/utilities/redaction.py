import typing


class SecretRedactionUtility:
    """Masks sensitive fields in headers and text to prevent logging secrets."""
    
    SENSITIVE_KEYS: typing.ClassVar[set[str]] = {
        "authorization", "cookie", "set-cookie", "password", "passwd",
        "token", "secret", "api_key", "access_token"
    }
    
    def redact_headers(self, headers: dict[str, str]) -> dict[str, str]:
        redacted = {}
        for k, v in headers.items():
            if k.lower() in self.SENSITIVE_KEYS:
                redacted[k] = self._mask_value(v)
            else:
                redacted[k] = v
        return redacted
        
    def _mask_value(self, value: str) -> str:
        if not value: return ""
        if len(value) <= 8:
            return "*" * len(value)
        return value[:4] + "*" * (len(value) - 8) + value[-4:]

secret_redaction = SecretRedactionUtility()
