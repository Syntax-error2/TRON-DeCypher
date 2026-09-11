try:
    import yara
    HAS_YARA = True
except ImportError:
    HAS_YARA = False

class YaraFoundationService:
    """Stub integration for optional YARA support."""
    
    def is_available(self) -> bool:
        return HAS_YARA
        
    def scan_file(self, filepath: str, rules_path: str) -> list[str]:
        if not HAS_YARA:
            return []
            
        try:
            # We don't download rules. We only use local if provided.
            rules = yara.compile(filepath=rules_path)
            matches = rules.match(filepath)
            return [str(m.rule) for m in matches]
        except Exception:
            return []

yara_foundation_service = YaraFoundationService()
