with open('app/ui/views/settings_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('\t', '    ')

with open('app/ui/views/settings_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
