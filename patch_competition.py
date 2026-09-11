import re

with open('app/ui/views/competition_dashboard_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add knowledge frame to active_layout
knowledge_patch = '''
        # CTF Knowledge Guidance
        kn_frame = QFrame()
        kn_frame.setFrameShape(QFrame.Shape.StyledPanel)
        kn_layout = QVBoxLayout(kn_frame)
        
        self.lbl_kn_cat = QLabel("<b>Challenge Category:</b> None")
        self.lbl_kn_topics = QLabel("Relevant Topics: None")
        self.lbl_kn_modules = QLabel("Recommended Modules: None")
        self.lbl_kn_sources = QLabel("Source References: None")
        
        btn_kn_open = QPushButton("Open CTF Knowledge")
        btn_kn_open.clicked.connect(lambda: self.navigate_requested.emit("CTF Knowledge"))
        
        kn_layout.addWidget(self.lbl_kn_cat)
        kn_layout.addWidget(self.lbl_kn_topics)
        kn_layout.addWidget(self.lbl_kn_modules)
        kn_layout.addWidget(self.lbl_kn_sources)
        kn_layout.addWidget(btn_kn_open)
        
        active_layout.addWidget(QLabel("<b>CTF Knowledge Guidance</b>"))
        active_layout.addWidget(kn_frame)
        
        self.stack.addWidget(self.active_widget)
'''
content = content.replace("        self.stack.addWidget(self.active_widget)", knowledge_patch)

# Update refresh metrics to also refresh knowledge
refresh_metrics_patch = '''
    def refresh_metrics(self) -> None:
        if not self.current_case_id:
            return
            
        metrics = competition_service.get_dashboard_metrics(self.current_case_id)
        for key, val in metrics.items():
            if key in self.metric_labels:
                self.metric_labels[key].setText(str(val))
                
        # Update CTF Knowledge Guidance
        from app.database.database import db
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT challenge_category FROM cases WHERE id = ?", (self.current_case_id,))
            row = cursor.fetchone()
            category = row['challenge_category'] if row and row['challenge_category'] else None
            
        if category:
            self.lbl_kn_cat.setText(f"<b>Challenge Category:</b> {category}")
            
            # Simple static mapping based on category for topics and modules
            mapping = {
                "Cryptography": ("Caesar, RSA, AES, Hash Cracking", "Decoder, Crypto", "Getting Started with CTF Challenges"),
                "Web": ("SQLi, XSS, Directory Traversal, Command Injection", "Web, Decoder", "Getting Started with CTF Challenges, CTF Master Cheatsheet"),
                "Forensics": ("Metadata, File Headers, Memory, PCAP", "Forensics, Quick Triage, Network", "Getting Started with CTF Challenges"),
                "Steganography": ("LSB, Bitplanes, Audio Spectrogram", "Stego", "CTF Master Cheatsheet"),
                "Reverse Engineering": ("Disassembly, Decompilation, Strings", "Binary, Malware Static Triage", "Getting Started with CTF Challenges"),
                "OSINT": ("Google Dorks, Exif, Search", "OSINT", "CTF Master Cheatsheet"),
                "Network": ("PCAP, Port Scanning, Netcat", "Network", "CTF Master Cheatsheet"),
                "Miscellaneous": ("Encoding, Basic scripts", "Decoder", "CTF Master Cheatsheet")
            }
            if category in mapping:
                tops, mods, srcs = mapping[category]
                self.lbl_kn_topics.setText(f"Relevant Topics: {tops}")
                self.lbl_kn_modules.setText(f"Recommended Modules: {mods}")
                self.lbl_kn_sources.setText(f"Source References: {srcs}")
            else:
                self.lbl_kn_topics.setText("Relevant Topics: Review challenge details")
                self.lbl_kn_modules.setText("Recommended Modules: Review challenge details")
                self.lbl_kn_sources.setText("Source References: Search knowledge base")
        else:
            self.lbl_kn_cat.setText("<b>Challenge Category:</b> Unspecified")
'''
content = content.replace('''
    def refresh_metrics(self) -> None:
        if not self.current_case_id:
            return
            
        metrics = competition_service.get_dashboard_metrics(self.current_case_id)
        for key, val in metrics.items():
            if key in self.metric_labels:
                self.metric_labels[key].setText(str(val))
''', refresh_metrics_patch)

with open('app/ui/views/competition_dashboard_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
