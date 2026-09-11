with open('app/knowledge/knowledge_service.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'import re' not in content:
    content = "import re\n" + content

with open('app/knowledge/knowledge_service.py', 'w', encoding='utf-8') as f:
    f.write(content)
