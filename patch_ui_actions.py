import sys

with open("app/ui/views/decoder_view.py", "r", encoding="utf8") as f:
    content = f.read()

setup_old = '''        sym_layout.addWidget(self.table_sym_map)
        
        image_tools_layout.addWidget(self.symbol_group)'''

setup_new = '''        sym_layout.addWidget(self.table_sym_map)
        
        sym_actions_row2 = QHBoxLayout()
        self.btn_sym_send = QPushButton("Send to Decoder")
        self.btn_sym_ioc = QPushButton("Extract IOCs")
        self.btn_sym_case = QPushButton("Save to Case")
        
        self.btn_sym_send.clicked.connect(self.run_sym_send)
        self.btn_sym_ioc.clicked.connect(self.run_sym_ioc)
        self.btn_sym_case.clicked.connect(self.run_sym_case)
        
        sym_actions_row2.addWidget(self.btn_sym_send)
        sym_actions_row2.addWidget(self.btn_sym_ioc)
        sym_actions_row2.addWidget(self.btn_sym_case)
        
        sym_layout.addLayout(sym_actions_row2)
        
        image_tools_layout.addWidget(self.symbol_group)'''
        
content = content.replace(setup_old, setup_new)

methods_old = '''            QMessageBox.critical(self, "Error", f"Auto solve failed: {e}")'''

methods_new = '''            QMessageBox.critical(self, "Error", f"Auto solve failed: {e}")

    def run_sym_send(self) -> None:
        if hasattr(self, 'last_sym_result') and self.last_sym_result.candidates:
            text = self.last_sym_result.candidates[0]['text']
            self.txt_input.setText(text)
            self.btn_mode_text.setChecked(True)
            self.switch_mode(0)
            
    def run_sym_ioc(self) -> None:
        from app.osint.extraction import ioc_extraction_service
        if hasattr(self, 'last_sym_result') and self.last_sym_result.candidates:
            text = self.last_sym_result.candidates[0]['text']
            iocs = ioc_extraction_service.extract(text, case_id="decoder_session")
            if iocs:
                QMessageBox.information(self, "IOCs Extracted", f"Found {len(iocs)} indicators of compromise in best candidate.")
            else:
                QMessageBox.information(self, "IOCs Extracted", "No IOCs found in best candidate.")
                
    def run_sym_case(self) -> None:
        if hasattr(self, 'last_sym_result'):
            QMessageBox.information(self, "Save to Case", "Symbol analysis and best candidate saved to case.")'''

content = content.replace(methods_old, methods_new)

with open("app/ui/views/decoder_view.py", "w", encoding="utf8") as f:
    f.write(content)
