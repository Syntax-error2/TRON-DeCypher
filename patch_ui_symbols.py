import sys

with open("app/ui/views/decoder_view.py", "r", encoding="utf8") as f:
    content = f.read()
    
# Import QTableWidget and QHeaderView if missing
if "QTableWidget" not in content:
    content = content.replace("QTableWidgetItem", "QTableWidget, QTableWidgetItem, QHeaderView")

# We want to add Symbol Analysis components.
setup_old = '''        img_actions_row.addWidget(self.btn_img_meta)
        img_actions_row.addWidget(self.btn_img_ioc)
        
        image_tools_layout.addLayout(img_actions_row)
        self.tools_stack.addWidget(image_tools_group)'''

setup_new = '''        img_actions_row.addWidget(self.btn_img_meta)
        img_actions_row.addWidget(self.btn_img_ioc)
        
        image_tools_layout.addLayout(img_actions_row)
        
        # Symbol / Image Cipher Integration
        self.symbol_group = QGroupBox("SYMBOL / IMAGE CIPHER")
        sym_layout = QVBoxLayout(self.symbol_group)
        
        sym_actions_row = QHBoxLayout()
        self.btn_sym_detect = QPushButton("Detect Symbols")
        self.combo_sym_profile = QComboBox()
        self.combo_sym_profile.addItems(["auto", "egyptian", "braille", "runes", "pigpen", "custom"])
        self.btn_sym_solve = QPushButton("Auto Solve")
        
        self.btn_sym_detect.clicked.connect(self.run_sym_detect)
        self.btn_sym_solve.clicked.connect(self.run_sym_solve)
        
        sym_actions_row.addWidget(self.btn_sym_detect)
        sym_actions_row.addWidget(QLabel("Profile:"))
        sym_actions_row.addWidget(self.combo_sym_profile)
        sym_actions_row.addWidget(self.btn_sym_solve)
        
        sym_layout.addLayout(sym_actions_row)
        
        self.table_sym_map = QTableWidget(0, 3)
        self.table_sym_map.setHorizontalHeaderLabels(["Symbol ID", "Assigned Char", "Count"])
        self.table_sym_map.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_sym_map.setFixedHeight(120)
        
        sym_layout.addWidget(self.table_sym_map)
        
        image_tools_layout.addWidget(self.symbol_group)
        self.tools_stack.addWidget(image_tools_group)'''

content = content.replace(setup_old, setup_new)

# Add run methods
methods_str = '''    def run_img_ioc(self) -> None:
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText("[Extract IOCs] No IOCs found directly in image envelope.")'''

methods_new = '''    def run_img_ioc(self) -> None:
        self.output_stack.setCurrentIndex(0)
        self.txt_output.setText("[Extract IOCs] No IOCs found directly in image envelope.")

    def run_sym_detect(self) -> None:
        if not self.current_image_path:
            QMessageBox.warning(self, "No Image", "Load an image first.")
            return
            
        try:
            from app.decoders.symbols import symbol_analysis_service
            # Initial run to get symbols without custom mapping
            self.last_sym_result = symbol_analysis_service.analyze_image(
                self.current_image_path, 
                profile_id=self.combo_sym_profile.currentText()
            )
            
            # Populate table
            unique_ids = set()
            counts = {}
            for s in self.last_sym_result.detected_symbols:
                unique_ids.add(s.symbol_id)
                counts[s.symbol_id] = counts.get(s.symbol_id, 0) + 1
                
            self.table_sym_map.setRowCount(len(unique_ids))
            for i, sid in enumerate(sorted(unique_ids)):
                self.table_sym_map.setItem(i, 0, QTableWidgetItem(sid))
                # Initial mapping char
                mapped = self.last_sym_result.mapping_used.get(sid, "")
                self.table_sym_map.setItem(i, 1, QTableWidgetItem(mapped))
                self.table_sym_map.setItem(i, 2, QTableWidgetItem(str(counts[sid])))
                
            self.txt_output.setText(f"Detected {len(self.last_sym_result.detected_symbols)} symbols ({len(unique_ids)} unique).")
            self.output_stack.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Symbol detection failed: {e}")
            
    def run_sym_solve(self) -> None:
        if not hasattr(self, 'last_sym_result'):
            QMessageBox.warning(self, "Run Detect First", "Please detect symbols first.")
            return
            
        # Build custom mapping from table
        custom_mapping = {}
        for r in range(self.table_sym_map.rowCount()):
            sid = self.table_sym_map.item(r, 0).text()
            val = self.table_sym_map.item(r, 1).text().strip()
            if val:
                custom_mapping[sid] = val
                
        try:
            from app.decoders.symbols import symbol_analysis_service
            self.last_sym_result = symbol_analysis_service.analyze_image(
                self.current_image_path, 
                profile_id=self.combo_sym_profile.currentText(),
                custom_mapping=custom_mapping
            )
            
            out = "--- SYMBOL CIPHER CANDIDATES ---\n\n"
            for c in self.last_sym_result.candidates[:5]:
                marker = " [FLAG CANDIDATE]" if "CTF{" in c['text'] or "FLAG{" in c['text'] or "TRON{" in c['text'] else ""
                out += f"Direction: {c['direction'].upper()} | Type: {c['type']} | Score: {c['score']:.2f}{marker}\n"
                out += f"{c['text']}\n\n"
                
            self.txt_output.setText(out)
            self.output_stack.setCurrentIndex(0)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Auto solve failed: {e}")'''

content = content.replace(methods_str, methods_new)

with open("app/ui/views/decoder_view.py", "w", encoding="utf8") as f:
    f.write(content)
