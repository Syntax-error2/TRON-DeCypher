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
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.memory.integrations.volatility_integration import volatility_integration_service
from app.memory.services.memory_analysis_service import memory_analysis_service


class MemoryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_filepath = ""
        self.current_result: Any = None
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # --- Top Controls ---
        ctrl_layout = QHBoxLayout()
        self.btn_load = QPushButton("Load Memory Dump")
        self.btn_load.clicked.connect(self.load_memory)
        
        status_text = "No image loaded."
        if volatility_integration_service.is_available():
            status_text += f" (Volatility3 detected at {volatility_integration_service.vol_path})"
        else:
            status_text += " (Volatility3 NOT found - minimal offline mode)"
            
        self.lbl_status = QLabel(status_text)
        
        ctrl_layout.addWidget(self.btn_load)
        ctrl_layout.addWidget(self.lbl_status)
        ctrl_layout.addStretch()
        
        main_layout.addLayout(ctrl_layout)
        
        # --- Tabs ---
        self.tabs = QTabWidget()
        
        self.tab_overview = QTextEdit()
        self.tab_overview.setReadOnly(True)
        self.tabs.addTab(self.tab_overview, "Overview")
        
        self.tab_processes = QTableWidget()
        self.tab_processes.setColumnCount(4)
        self.tab_processes.setHorizontalHeaderLabels(["PID", "PPID", "Name", "Start Time"])
        self.tabs.addTab(self.tab_processes, "Processes")
        
        self.tab_process_tree = QTreeWidget()
        self.tab_process_tree.setHeaderLabels(["Process Name", "PID"])
        self.tabs.addTab(self.tab_process_tree, "Process Tree")
        
        self.tab_network = QTableWidget()
        self.tab_network.setColumnCount(6)
        self.tab_network.setHorizontalHeaderLabels(["Process", "PID", "Protocol", "Local", "Foreign", "State"])
        self.tabs.addTab(self.tab_network, "Network")
        
        self.tab_modules = QTableWidget()
        self.tab_modules.setColumnCount(5)
        self.tab_modules.setHorizontalHeaderLabels(["Process", "PID", "Module", "Base", "Path"])
        self.tabs.addTab(self.tab_modules, "Modules")
        
        self.tab_strings = QTextEdit()
        self.tab_strings.setReadOnly(True)
        self.tabs.addTab(self.tab_strings, "Strings")
        
        main_layout.addWidget(self.tabs)
        
    def load_memory(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Memory Image")
        if not file_path:
            return
            
        self.current_filepath = file_path
        self.lbl_status.setText(f"Loading: {file_path} ...")
        
        try:
            self.current_result = memory_analysis_service.analyze(file_path)
            self.populate_ui()
            self.lbl_status.setText(f"Loaded: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", str(e))
            self.lbl_status.setText("Load failed.")
            
    def populate_ui(self) -> None:
        if not self.current_result: return
        res = self.current_result
        
        # Overview
        ov = f"OS Hint: {res.os_hint}\n"
        ov += f"Architecture Hint: {res.architecture_hint}\n"
        ov += f"Size: {res.size_bytes} bytes\n\n"
        
        ov += f"Processes: {len(res.processes)}\n"
        ov += f"Connections: {len(res.connections)}\n"
        ov += f"Modules: {len(res.modules)}\n"
        ov += f"Extracted IOCs: {res.iocs_extracted}\n\n"
        
        ov += "--- Findings ---\n"
        for f in res.findings:
            ov += f"[{f.severity}] {f.source}: {f.description}\n"
            
        self.tab_overview.setText(ov)
        
        # Processes
        self.tab_processes.setRowCount(len(res.processes))
        for row, p in enumerate(res.processes):
            self.tab_processes.setItem(row, 0, QTableWidgetItem(str(p.pid)))
            self.tab_processes.setItem(row, 1, QTableWidgetItem(str(p.ppid)))
            self.tab_processes.setItem(row, 2, QTableWidgetItem(p.name))
            self.tab_processes.setItem(row, 3, QTableWidgetItem(p.start_time))
            
        # Process Tree
        self.tab_process_tree.clear()
        nodes = {}
        # First pass: create nodes
        for p in res.processes:
            item = QTreeWidgetItem([p.name, str(p.pid)])
            nodes[p.pid] = (item, p.ppid)
            
        # Second pass: attach to parents
        for pid, (item, ppid) in nodes.items():
            if ppid in nodes and ppid != pid:
                nodes[ppid][0].addChild(item)
            else:
                self.tab_process_tree.addTopLevelItem(item)
        self.tab_process_tree.expandAll()
        
        # Network
        self.tab_network.setRowCount(len(res.connections))
        for row, c in enumerate(res.connections):
            self.tab_network.setItem(row, 0, QTableWidgetItem(c.process_name))
            self.tab_network.setItem(row, 1, QTableWidgetItem(str(c.pid)))
            self.tab_network.setItem(row, 2, QTableWidgetItem(c.protocol))
            self.tab_network.setItem(row, 3, QTableWidgetItem(f"{c.source_ip}:{c.source_port}"))
            self.tab_network.setItem(row, 4, QTableWidgetItem(f"{c.dest_ip}:{c.dest_port}"))
            self.tab_network.setItem(row, 5, QTableWidgetItem(c.state))
            
        # Modules
        self.tab_modules.setRowCount(len(res.modules))
        for row, m in enumerate(res.modules):
            self.tab_modules.setItem(row, 0, QTableWidgetItem(m.process_name))
            self.tab_modules.setItem(row, 1, QTableWidgetItem(str(m.pid)))
            self.tab_modules.setItem(row, 2, QTableWidgetItem(m.name))
            self.tab_modules.setItem(row, 3, QTableWidgetItem(str(m.base_address)))
            self.tab_modules.setItem(row, 4, QTableWidgetItem(m.path))
            
        # Strings
        s_out = "\n".join([s["string"] for s in res.strings[:1000]])
        if len(res.strings) > 1000:
            s_out += f"\n... and {len(res.strings)-1000} more strings."
        self.tab_strings.setText(s_out)

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
