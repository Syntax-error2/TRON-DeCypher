with open('app/ui/views/competition_dashboard_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
        self.lbl_status = QLabel("STATUS: STOPPED")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        from app.core.config import settings
        self.lbl_flag_format = QLabel(f"<b>Flag Format:</b> {settings.flag_pattern}")
        self.lbl_flag_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
'''
content = content.replace('''
        self.lbl_status = QLabel("STATUS: STOPPED")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
''', patch.lstrip())

patch2 = '''
        active_layout.addWidget(self.lbl_time)
        active_layout.addWidget(self.lbl_status)
        active_layout.addWidget(self.lbl_flag_format)
'''
content = content.replace('''
        active_layout.addWidget(self.lbl_time)
        active_layout.addWidget(self.lbl_status)
''', patch2.lstrip())

with open('app/ui/views/competition_dashboard_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
