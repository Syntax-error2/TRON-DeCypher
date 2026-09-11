with open('app/knowledge/seeder.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('def seed_knowledge_base():', 'def seed_knowledge_base() -> None:')

with open('app/knowledge/seeder.py', 'w', encoding='utf-8') as f:
    f.write(content)
