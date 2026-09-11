from typing import Any

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.binary.services.binary_analysis_service import binary_analysis_service
from app.binary.services.disassembly_service import HAS_CAPSTONE, disassembly_service
from app.ui.views.knowledge_panel import KnowledgePanel


class BinaryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_filepath = ""
        self.current_result: Any = None
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        # --- Top Controls ---
        ctrl_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load Local Binary")
        self.btn_load.clicked.connect(self.load_binary)

        self.lbl_status = QLabel("No binary loaded.")

        ctrl_layout.addWidget(self.btn_load)
        ctrl_layout.addWidget(self.lbl_status)
        ctrl_layout.addStretch()

        main_layout.addLayout(ctrl_layout)

        # --- Tabs ---
        self.tabs = QTabWidget()

        self.tab_overview = QTextEdit()
        self.tab_overview.setReadOnly(True)
        self.tabs.addTab(self.tab_overview, "Overview")

        self.tab_sections = QTableWidget()
        self.tab_sections.setColumnCount(7)
        self.tab_sections.setHorizontalHeaderLabels(["Name", "VAddr", "VSize", "Raw Size", "Offset", "Entropy", "Perms"])
        self.tabs.addTab(self.tab_sections, "Sections")

        self.tab_imports = QTableWidget()
        self.tab_imports.setColumnCount(4)
        self.tab_imports.setHorizontalHeaderLabels(["Library", "Function", "Address", "Category"])
        self.tabs.addTab(self.tab_imports, "Imports")

        self.tab_strings = QTextEdit()
        self.tab_strings.setReadOnly(True)
        self.tabs.addTab(self.tab_strings, "Strings")

        self.tab_disasm = QWidget()
        self.setup_disasm_tab()
        self.tabs.addTab(self.tab_disasm, "Disassembly (Preview)")

        main_layout.addWidget(self.tabs)

        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("Disassembly Decompilation Ghidra Strings")
        main_layout.addWidget(self.kn_panel)


    def setup_disasm_tab(self) -> None:
        layout = QVBoxLayout(self.tab_disasm)
        self.txt_disasm = QTextEdit()
        self.txt_disasm.setReadOnly(True)

        if not HAS_CAPSTONE:
            self.txt_disasm.setText("Capstone is not installed. Disassembly is unavailable.")

        layout.addWidget(self.txt_disasm)

    def load_binary(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Binary")
        if not file_path:
            return

        self.current_filepath = file_path
        self.lbl_status.setText(f"Loaded: {file_path}")

        try:
            self.current_result = binary_analysis_service.analyze(file_path)
            self.populate_ui()
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", str(e))

    def populate_ui(self) -> None:
        if not self.current_result: return
        res = self.current_result

        # Overview
        ov = f"Format: {res.format}\n"
        ov += f"Architecture: {res.architecture} ({res.bitness})\n"
        ov += f"Endianness: {res.endianness}\n"
        ov += f"Entry Point: {hex(res.entry_point) if res.entry_point else 'Unknown'}\n"
        ov += f"Overall Entropy: {res.entropy:.2f}\n"
        ov += f"Packed/Obfuscated Hint: {res.is_packed_hint}\n\n"

        ov += "--- Protections ---\n"
        ov += f"NX (DEP): {res.protections.nx}\n"
        ov += f"PIE: {res.protections.pie}\n"

        ov += "\n--- Findings ---\n"
        for f in res.findings:
            ov += f"- {f}\n"

        self.tab_overview.setText(ov)

        # Sections
        self.tab_sections.setRowCount(len(res.sections))
        for row, sec in enumerate(res.sections):
            self.tab_sections.setItem(row, 0, QTableWidgetItem(sec.name))
            self.tab_sections.setItem(row, 1, QTableWidgetItem(hex(sec.virtual_address)))
            self.tab_sections.setItem(row, 2, QTableWidgetItem(str(sec.virtual_size)))
            self.tab_sections.setItem(row, 3, QTableWidgetItem(str(sec.raw_size)))
            self.tab_sections.setItem(row, 4, QTableWidgetItem(hex(sec.offset)))
            self.tab_sections.setItem(row, 5, QTableWidgetItem(f"{sec.entropy:.2f}"))
            self.tab_sections.setItem(row, 6, QTableWidgetItem(sec.permissions))

        # Imports
        self.tab_imports.setRowCount(len(res.imports))
        for row, imp in enumerate(res.imports):
            self.tab_imports.setItem(row, 0, QTableWidgetItem(imp.library))
            self.tab_imports.setItem(row, 1, QTableWidgetItem(imp.function))
            self.tab_imports.setItem(row, 2, QTableWidgetItem(hex(imp.address)))
            self.tab_imports.setItem(row, 3, QTableWidgetItem(imp.category))

        # Strings
        s_out = "\n".join([s["string"] for s in res.strings[:1000]])  # cap at 1000 for UI
        if len(res.strings) > 1000:
            s_out += f"\n... and {len(res.strings)-1000} more strings."
        self.tab_strings.setText(s_out)

        # Disassembly Preview
        if HAS_CAPSTONE and res.entry_point:
            try:
                # Need to read raw bytes from the entry point if we can translate it to an offset.
                # Since RVA to Offset mapping can be tricky, for this safe preview we just read the first 256 bytes of the file
                # or if it's ELF/PE we'd ideally read the section containing the EP.

                # For this proof of concept, we just read the first executable section's data.
                exec_sec = next((s for s in res.sections if "X" in s.permissions), None)
                if exec_sec and exec_sec.raw_size > 0:
                    with open(self.current_filepath, 'rb') as f:
                        f.seek(exec_sec.offset)
                        data = f.read(min(256, exec_sec.raw_size))

                    instructions = disassembly_service.disassemble(data, res.architecture, exec_sec.virtual_address)
                    d_out = f"; Disassembly Preview of {exec_sec.name} section:\n\n"
                    for i in instructions:
                        d_out += f"{hex(i.address)}:  {i.bytes_hex:<20} {i.mnemonic}\t{i.operands}\n"
                    self.txt_disasm.setText(d_out)
                else:
                    self.txt_disasm.setText("No executable section found to preview disassembly.")
            except Exception as e:
                self.txt_disasm.setText(f"Disassembly failed: {e}")

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
