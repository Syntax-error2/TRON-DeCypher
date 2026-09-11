from pathlib import Path


class KnowledgeRegistry:
    def __init__(self):
        self.base_dir = Path("app/knowledge")
        self.dict_dir = self.base_dir / "dictionaries"
        
    def get_category_wordlist(self, category: str) -> list[str]:
        cat_file = self.dict_dir / f"ctf_{category.lower()}.txt"
        if cat_file.exists():
            return self._load_file(cat_file)
        return []
        
    def get_master_wordlist(self) -> list[str]:
        master = self.dict_dir / "tron_ctf_master.txt"
        if master.exists():
            return self._load_file(master)
        return []

    def get_tron_context_wordlist(self) -> list[str]:
        return self._load_file(self.dict_dir / "ctf_tron_context.txt")
        
    def _load_file(self, path: Path) -> list[str]:
        if not path.exists():
            return []
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return [line.strip() for line in f if line.strip()]

knowledge_registry = KnowledgeRegistry()
