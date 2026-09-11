import sys
import re

with open("app/ui/views/decoder_view.py", "r", encoding="utf8") as f:
    content = f.read()

# 1. Add QFormLayout, QWidget to imports if missing
if "QFormLayout" not in content:
    content = content.replace("QVBoxLayout,", "QVBoxLayout, QFormLayout,")
if "QCheckBox" not in content:
    content = content.replace("QPushButton,", "QPushButton, QCheckBox,")

# 2. Re-write setup for combo_decoders and add parameter container
setup_old = '''        self.combo_decoders = QComboBox()
        self.all_decoders = [d.name for d in decoder_registry.list_all()]
        self.combo_decoders.addItems(self.all_decoders)
            
        self.btn_add_step = QPushButton("+ Add Step")'''

setup_new = '''        self.combo_decoders = QComboBox()
        self.all_decoders = []
        self._category_map = {
            "encoding": "ENCODING",
            "classical_ciphers": "CLASSICAL CIPHERS",
            "numeric": "NUMERIC / BITWISE",
            "text": "TEXT / WEB",
            "hash": "HASH ANALYSIS"
        }
        
        # Build categorized list
        cat_dict = {}
        for d in decoder_registry.list_all():
            cat = self._category_map.get(d.category, d.category.upper())
            if cat not in cat_dict:
                cat_dict[cat] = []
            cat_dict[cat].append(d.name)
            self.all_decoders.append(d.name)
            
        for cat, names in cat_dict.items():
            self.combo_decoders.addItem(f"--- {cat} ---")
            for name in sorted(names):
                self.combo_decoders.addItem(name)
                
        self.combo_decoders.currentIndexChanged.connect(self.on_decoder_selected)
        
        self.param_container = QWidget()
        self.param_layout = QFormLayout(self.param_container)
        self.param_inputs = {}
            
        self.btn_add_step = QPushButton("+ Add Step")'''
        
content = content.replace(setup_old, setup_new)

# 3. Insert param_container into UI layout
layout_old = '''        pipeline_ctrls.addWidget(self.btn_clear_pipeline)
        pipeline_layout.addLayout(pipeline_ctrls)
        self.tools_stack.addWidget(pipeline_group)'''
layout_new = '''        pipeline_ctrls.addWidget(self.btn_clear_pipeline)
        pipeline_layout.addLayout(pipeline_ctrls)
        pipeline_layout.addWidget(self.param_container)
        self.tools_stack.addWidget(pipeline_group)'''
content = content.replace(layout_old, layout_new)

# 4. Modify add_pipeline_step
add_old = '''    def add_pipeline_step(self) -> None:
        decoder_name = self.combo_decoders.currentText()
        if not decoder_name:
            return
        
        d_obj = decoder_registry.get(decoder_name)
        if d_obj and not getattr(d_obj, "reversible", True):
            QMessageBox.warning(self, "One-Way Function", f"{decoder_name} is a one-way function and should not be used in reversible pipelines.")
            
        step = TransformationStep(
            id=uuid.uuid4().hex[:8],
            decoder_name=decoder_name,
            parameters={}
        )'''
add_new = '''    def add_pipeline_step(self) -> None:
        decoder_name = self.combo_decoders.currentText()
        if not decoder_name or decoder_name.startswith("---"):
            return
        
        d_obj = decoder_registry.get(decoder_name)
        if d_obj and not getattr(d_obj, "reversible", True):
            QMessageBox.warning(self, "One-Way Function", f"{decoder_name} is a one-way function and should not be used in reversible pipelines.")
            
        params = {}
        for key, widget in self.param_inputs.items():
            if isinstance(widget, QLineEdit):
                params[key] = widget.text()
            elif isinstance(widget, QCheckBox):
                params[key] = widget.isChecked()
            
        step = TransformationStep(
            id=uuid.uuid4().hex[:8],
            decoder_name=decoder_name,
            parameters=params
        )'''
content = content.replace(add_old, add_new)

# 5. Add on_decoder_selected and fix filter_decoders
methods_str = '''    def filter_decoders(self, text: str) -> None:
        text = text.lower()
        self.combo_decoders.clear()
        if not text:
            self.combo_decoders.addItems(self.all_decoders)
            return
        filtered = [d for d in self.all_decoders if text in d.lower()]
        self.combo_decoders.addItems(filtered)'''
methods_new = '''    def on_decoder_selected(self) -> None:
        while self.param_layout.count():
            item = self.param_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.param_inputs.clear()
        
        decoder_name = self.combo_decoders.currentText()
        if not decoder_name or decoder_name.startswith("---"):
            return
            
        d_obj = decoder_registry.get(decoder_name)
        if not d_obj:
            return
            
        params = getattr(d_obj, "expected_params", {})
        for key, info in params.items():
            ptype = info.get("type", "str")
            pdesc = info.get("description", key)
            pdef = info.get("default", "")
            
            if ptype == "bool":
                chk = QCheckBox(pdesc)
                chk.setChecked(bool(pdef))
                self.param_layout.addRow("", chk)
                self.param_inputs[key] = chk
            else:
                txt = QLineEdit()
                txt.setText(str(pdef))
                self.param_layout.addRow(f"{pdesc}:", txt)
                self.param_inputs[key] = txt

    def filter_decoders(self, text: str) -> None:
        text = text.lower()
        self.combo_decoders.clear()
        if not text:
            # Rebuild categorized
            cat_dict = {}
            for d in decoder_registry.list_all():
                cat = self._category_map.get(d.category, d.category.upper())
                if cat not in cat_dict:
                    cat_dict[cat] = []
                cat_dict[cat].append(d.name)
            for cat, names in cat_dict.items():
                self.combo_decoders.addItem(f"--- {cat} ---")
                for name in sorted(names):
                    self.combo_decoders.addItem(name)
            return
            
        filtered = [d for d in self.all_decoders if text in d.lower()]
        self.combo_decoders.addItems(filtered)'''
content = content.replace(methods_str, methods_new)

with open("app/ui/views/decoder_view.py", "w", encoding="utf8") as f:
    f.write(content)
