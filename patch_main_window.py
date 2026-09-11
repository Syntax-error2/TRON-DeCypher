import re

with open('app/ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add to nav_items
content = content.replace(
    '            "OSINT", \n',
    '            "OSINT", "CTF Knowledge", \n'
)

# Add to create_view
create_view_patch = '''
        elif title == "Settings":
            from app.ui.views.settings_view import SettingsView
            return SettingsView()
        elif title == "CTF Knowledge":
            from app.ui.views.knowledge_view import CTFKnowledgeView
            return CTFKnowledgeView()
'''
content = content.replace('''
        elif title == "Settings":
            from app.ui.views.settings_view import SettingsView
            return SettingsView()
''', create_view_patch)

# Add to command palette
content = content.replace(
    '            "OSINT", "AI Copilot"',
    '            "OSINT", "CTF Knowledge", "AI Copilot"'
)

with open('app/ui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)
