import re

with open('app/ui/main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    def open_command_palette(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Command Palette")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        items = ["Import Artifact", "Quick Triage", "Open Decoder", "Add Bookmark", "Add Note", "Generate Report"]
        list_widget.addItems(items)
        layout.addWidget(list_widget)
        
        def on_accept() -> None:
            dialog.accept()
            
        list_widget.itemDoubleClicked.connect(on_accept)
        dialog.exec()'''

replacement = '''    def open_command_palette(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Command Palette")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        inp = QLineEdit()
        inp.setPlaceholderText("Type to filter...")
        layout.addWidget(inp)
        
        list_widget = QListWidget()
        items = [
            "New Case", "Open Case", "Competition Dashboard", "Import Artifact", 
            "Quick Triage", "Decoder", "Forensics", "Steganography", 
            "Network", "Crypto", "Web", "Binary", "Memory", "Malware Static Triage", 
            "OSINT", "AI Copilot", "Tools", "Settings", 
            "Add Note", "Add Task", "Add Flag", "Generate Report"
        ]
        list_widget.addItems(items)
        layout.addWidget(list_widget)
        
        def filter_items(text):
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setHidden(text.lower() not in item.text().lower())
                
        inp.textChanged.connect(filter_items)
        
        def on_accept() -> None:
            curr = list_widget.currentItem()
            if curr:
                action = curr.text()
                dialog.accept()
                
                # Navigate if it's a sidebar item
                nav_map = {
                    "Competition Dashboard": "Competition Dashboard",
                    "Open Case": "Case Workspace",
                    "Quick Triage": "Quick Triage",
                    "Decoder": "Decoder",
                    "Forensics": "Forensics",
                    "Steganography": "Steganography",
                    "Network": "Network",
                    "Crypto": "Crypto",
                    "Web": "Web",
                    "Binary": "Binary",
                    "Memory": "Memory",
                    "Malware Static Triage": "Malware Static Triage",
                    "OSINT": "OSINT",
                    "AI Copilot": "AI Copilot",
                    "Tools": "Tools",
                    "Settings": "Settings",
                    "New Case": "New Case"
                }
                if action in nav_map:
                    self.navigate_to_item(nav_map[action])
                elif action in ["Import Artifact", "Add Note", "Add Task", "Add Flag", "Generate Report"]:
                    self.navigate_to_item("Case Workspace")
                    # Optionally trigger specific dialogs here if implemented in CaseWorkspaceView
            
        list_widget.itemDoubleClicked.connect(on_accept)
        dialog.exec()'''

if target in content:
    content = content.replace(target, replacement)
    # also add QLineEdit import if missing
    if 'QLineEdit' not in content:
        content = content.replace('from PySide6.QtWidgets import (', 'from PySide6.QtWidgets import (\n    QLineEdit,')
    
    with open('app/ui/main_window.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Command Palette Patched")
else:
    print("Could not patch command palette")
