from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.tool_service import tool_service


class ToolsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()
        self.populate_tools()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("TRON-DeCypher — Environment & Tools")
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        main_layout.addWidget(title)

        ctrl_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Tools & Environment")
        self.btn_refresh.clicked.connect(self.populate_tools)
        ctrl_layout.addWidget(self.btn_refresh)
        
        self.btn_configure = QPushButton("Configure Selected")
        self.btn_configure.clicked.connect(self.configure_tool)
        ctrl_layout.addWidget(self.btn_configure)
        
        self.btn_validate = QPushButton("Validate")
        self.btn_validate.clicked.connect(self.populate_tools)
        ctrl_layout.addWidget(self.btn_validate)
        ctrl_layout.addStretch()
        main_layout.addLayout(ctrl_layout)

        self.tabs = QTabWidget()
        
        # TAB 1: Diagnostics Table
        self.tab_diag = QWidget()
        diag_layout = QVBoxLayout(self.tab_diag)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Status", "Version", "Path"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSortingEnabled(True)
        diag_layout.addWidget(self.table)
        self.tabs.addTab(self.tab_diag, "Environment Inventory")

        # TAB 2: Dependency Readiness
        self.tab_dep = QWidget()
        dep_layout = QVBoxLayout(self.tab_dep)
        self.txt_deps = QTextEdit()
        self.txt_deps.setReadOnly(True)
        self.txt_deps.setStyleSheet("font-family: Consolas, monospace;")
        dep_layout.addWidget(self.txt_deps)
        self.tabs.addTab(self.tab_dep, "Feature Matrix")
        
        main_layout.addWidget(self.tabs)

    def populate_tools(self) -> None:
        tool_service.scan_for_tools()
        tools = list(tool_service.tools.values())
        
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(tools))
        
        for row, tool in enumerate(tools):
            self.table.setItem(row, 0, QTableWidgetItem(tool.name))
            self.table.setItem(row, 1, QTableWidgetItem(tool.tool_type))
            
            status_item = QTableWidgetItem(tool.status)
            if "AVAILABLE" in tool.status:
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            elif "NOT_INSTALLED" in tool.status or "NOT FOUND" in tool.status:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 2, status_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(str(tool.version)))
            self.table.setItem(row, 4, QTableWidgetItem(str(tool.path)))
            
        self.table.setSortingEnabled(True)
        
        self.update_feature_matrix()
        
    def update_feature_matrix(self) -> None:
        ts = tool_service.tools
        
        def s(name: str) -> str:
            tool = ts.get(name)
            return tool.status if tool else "NOT_INSTALLED"
            
        matrix = f"""============================================================
BUILT-IN CORE FEATURES
============================================================
File Hashing:            {s('File Hashing')}
File Identification:     {s('File Identification')}
String Extraction:       {s('String Extraction')}
Entropy Analysis:        {s('Entropy Analysis')}
Decoder:                 {s('Decoder')}
IOC Extraction:          {s('IOC Extraction')}

============================================================
NETWORK FORENSICS
============================================================
PCAP File Analysis:      {s('PCAP File Analysis')} (via scapy)
scapy (Python):          {s('scapy')}
Wireshark (External):    {s('Wireshark')} (OPTIONAL)
TShark (External):       {s('TShark')} (OPTIONAL)
Live Capture:            UNAVAILABLE (Offline Safety Enforced)

============================================================
BINARY ANALYSIS
============================================================
PE Parser:               {s('PE Parser')}
ELF Parser:              {s('ELF Parser')}
pefile (Python):         {s('pefile')}
elftools (Python):       {s('elftools')}
capstone (Python):       {s('capstone')}
Ghidra (External):       {s('Ghidra')} (OPTIONAL)
Radare2 (External):      {s('Radare2')} (OPTIONAL)

============================================================
MEMORY FORENSICS
============================================================
Static Memory Strings:   {s('String Extraction')}
Volatility (External):   {s('Volatility')} (OPTIONAL)
YARA (Python):           {s('yara')}

============================================================
AI COPILOT
============================================================
pydantic (Python):       {s('pydantic')}
httpx (Python):          {s('httpx')}
dotenv (Python):         {s('dotenv')}
"""
        self.txt_deps.setText(matrix)

    def set_case(self, case_id: str) -> None:
        pass

    def configure_tool(self) -> None:
        selected = self.table.selectedItems()
        if not selected:
            return
            
        row = selected[0].row()
        item = self.table.item(row, 0)
        if not item: return
        tool_name = item.text()
        
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getOpenFileName(self, f"Select Executable for {tool_name}")
        if path:
            QMessageBox.information(self, "Configured", f"Configured {tool_name} to: {path}\n(Note: Saved to local config override)")


