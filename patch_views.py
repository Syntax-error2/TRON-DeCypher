import re

def patch_view(filepath, search_query):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Import KnowledgePanel
    if "from app.ui.views.knowledge_panel import KnowledgePanel" not in content:
        content = content.replace("class ", "from app.ui.views.knowledge_panel import KnowledgePanel\n\nclass ", 1)
        
    # Add to layout
    # Assuming layout is either main_layout, layout, splitter, etc.
    # Usually we can just append it to the bottom of the left panel or root layout.
    if "self.kn_panel = KnowledgePanel()" not in content:
        init_ui_idx = content.find("def init_ui(self)")
        if init_ui_idx == -1: return
        
        # We will append the panel at the end of init_ui
        # Find the end of init_ui by looking for the next def
        end_idx = content.find("def ", init_ui_idx + 10)
        if end_idx == -1: end_idx = len(content)
        
        init_ui_body = content[init_ui_idx:end_idx]
        
        # Determine the root layout to add it to.
        # It's usually layout.addWidget or main_layout.addWidget
        layout_name = "layout"
        if "main_layout = " in init_ui_body: layout_name = "main_layout"
        elif "splitter.addWidget(" in init_ui_body: layout_name = "splitter"
        
        patch = f'''
        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("{search_query}")
        {layout_name}.addWidget(self.kn_panel)
'''
        
        # Insert before the end of the init_ui block (before the last return or just at end of block)
        # We'll just insert it before the last line of init_ui
        lines = init_ui_body.split('\n')
        lines.insert(-2, patch)
        new_init_ui = '\n'.join(lines)
        
        content = content.replace(init_ui_body, new_init_ui)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

patch_view("app/ui/views/crypto_view.py", "RSA AES Caesar Hash Cracking")
patch_view("app/ui/views/forensics_view.py", "Metadata File Headers Carving")
patch_view("app/ui/views/web_view.py", "SQLi XSS Directory Traversal")
patch_view("app/ui/views/binary_view.py", "Disassembly Decompilation Ghidra Strings")
patch_view("app/ui/views/network_view.py", "PCAP Wireshark")
patch_view("app/ui/views/stego_view.py", "Steganography LSB bitplane")
