with open('app/knowledge/knowledge_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\ufeff', '')

with open('app/knowledge/knowledge_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
