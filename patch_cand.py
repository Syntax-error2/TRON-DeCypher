with open('app/services/candidate_generation.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('wrappers: list[str] = field(default_factory=lambda: ["CTF", "TRON", "FLAG"])', 'wrappers: list[str] = field(default_factory=lambda: ["CTK", "FLAG", "TRON"])')

with open('app/services/candidate_generation.py', 'w', encoding='utf-8') as f:
    f.write(content)
