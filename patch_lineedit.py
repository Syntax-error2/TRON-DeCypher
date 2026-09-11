import re
with open('app/ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'from PySide6.QtWidgets import (',
    'from PySide6.QtWidgets import (\n    QLineEdit,'
)

with open('app/ui/main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)
