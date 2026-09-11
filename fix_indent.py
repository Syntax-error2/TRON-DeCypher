with open('app/knowledge/knowledge_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
for i, line in enumerate(lines):
    if line.startswith('def _sanitize_fts_query'):
        lines[i] = '    ' + line
    elif line.startswith('class CTFKnowledgeService:'):
        # ensure next lines have indentation
        pass
        
with open('app/knowledge/knowledge_service.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
