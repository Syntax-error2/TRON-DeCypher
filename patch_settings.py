with open('app/ui/views/settings_view.py', 'r', encoding='utf-8') as f:
    content = f.read()

patch = '''
        app_form.addRow("Version:", QLabel(settings.app_version))
        self.inp_flag_pattern = QLineEdit(settings.flag_pattern)
        app_form.addRow("Flag Pattern:", self.inp_flag_pattern)
'''
content = content.replace('        app_form.addRow("Version:", QLabel(settings.app_version))', patch.lstrip())

save_patch = '''
            if self.inp_vt_key.text() != (settings.virustotal_api_key or ""):
                updates["VIRUSTOTAL_API_KEY"] = self.inp_vt_key.text()
            if self.inp_flag_pattern.text() != settings.flag_pattern:
                updates["FLAG_PATTERN"] = self.inp_flag_pattern.text()
                settings.flag_pattern = self.inp_flag_pattern.text()
'''
content = content.replace('            if self.inp_vt_key.text() != (settings.virustotal_api_key or ""):\n                updates["VIRUSTOTAL_API_KEY"] = self.inp_vt_key.text()', save_patch.strip('\n'))

with open('app/ui/views/settings_view.py', 'w', encoding='utf-8') as f:
    f.write(content)
