import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("TRON-DeCypher")
        import os
        import sys
        base_dir = getattr(sys, '_MEIPASS', os.path.abspath('.'))
        icon_path = os.path.join(base_dir, 'assets', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1200, 800)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: #d4d4d4; }
            QListWidget { background-color: #252526; color: #d4d4d4; border: none; padding: 5px; }
            QListWidget::item:selected { background-color: #37373d; }
            QLabel { color: #d4d4d4; }
        """)
        
        self.init_ui()
        logger.info("Main window initialized.")

    def init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        
        nav_items = [
            "Competition Dashboard", "Case Workspace", "Quick Triage", "Decoder", 
            "Forensics", "Network", "Crypto", "Steganography", 
            "Web", "Binary", "Memory", "Malware Static Triage", "OSINT", 
            "AI Copilot", "Tools", "Settings"
        ]
        self.sidebar.addItems(nav_items)
        
        self.content_area = QStackedWidget()
        self.content_area.setContentsMargins(20, 20, 20, 20)
        
        for item in nav_items:
            view = self.create_view(item)
            if hasattr(view, 'navigate_requested'):
                view.navigate_requested.connect(self.navigate_to_item)
            self.content_area.addWidget(view)
            
        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(separator)
        main_layout.addWidget(self.content_area)
        
        self.cmd_palette_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.cmd_palette_shortcut.activated.connect(self.open_command_palette)

        self.statusBar().showMessage("TRON-DeCypher initialized. Ready.")
        self.statusBar().setStyleSheet("background-color: #007acc; color: white;")
        
    def create_view(self, title: str) -> QWidget:
        if title == "Competition Dashboard":
            from app.ui.views.competition_dashboard_view import CompetitionDashboardView
            view = CompetitionDashboardView()
            view.case_activated.connect(self.set_active_case)
            return view
        elif title == "Case Workspace":
            from app.ui.views.case_workspace_view import CaseWorkspaceView
            return CaseWorkspaceView()
        elif title == "Quick Triage":
            from app.ui.views.triage_view import TriageView
            return TriageView()
        elif title == "Decoder":
            from app.ui.views.decoder_view import DecoderView
            return DecoderView()
        elif title == "Forensics":
            from app.ui.views.forensics_view import ForensicsView
            return ForensicsView()
        elif title == "Steganography":
            from app.ui.views.stego_view import StegoView
            return StegoView()
        elif title == "OSINT":
            from app.ui.views.osint_view import OsintView
            return OsintView()
        elif title == "Network":
            from app.ui.views.network_view import NetworkView
            return NetworkView()
        elif title == "Crypto":
            from app.ui.views.crypto_view import CryptoView
            return CryptoView()
        elif title == "Web":
            from app.ui.views.web_view import WebView
            return WebView()
        elif title == "Binary":
            from app.ui.views.binary_view import BinaryView
            return BinaryView()
        elif title == "Memory":
            from app.ui.views.memory_view import MemoryView
            return MemoryView()
        elif title == "Malware Static Triage":
            from app.ui.views.malware_triage_view import MalwareTriageView
            return MalwareTriageView()
        elif title == "AI Copilot":
            from app.ui.views.ai_copilot_view import AICopilotView
            return AICopilotView()
        elif title == "Tools":
            from app.ui.views.tools_view import ToolsView
            return ToolsView()
        elif title == "Settings":
            from app.ui.views.settings_view import SettingsView
            return SettingsView()
        elif title == "CTF Knowledge":
            from app.ui.views.knowledge_view import CTFKnowledgeView
            return CTFKnowledgeView()
            
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"{title} View")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = label.font()
        font.setPointSize(24)
        label.setFont(font)
        layout.addWidget(label)
        return widget

    def navigate_to_item(self, target: str) -> None:
        if target == "New Case":
            from app.services.case_service import case_service
            case = case_service.create_case("New_Investigation", "Created from Dashboard")
            if case:
                self.set_active_case(case.id)
                self.navigate_to_item("Case Workspace")
            return
            
        for i in range(self.sidebar.count()):
            if self.sidebar.item(i).text() == target:
                self.sidebar.setCurrentRow(i)
                return

    def set_active_case(self, case_id: str) -> None:
        logger.info(f"Setting active case context to: {case_id}")
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if widget and hasattr(widget, 'set_case'):
                try:
                    widget.set_case(case_id)
                except Exception as e:
                    logger.error(f"Failed to set case on {widget}: {e}")
        self.statusBar().showMessage(f"Active Case: {case_id}")

    def open_command_palette(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Command Palette")
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        inp = QLineEdit()
        inp.setPlaceholderText("Type to filter...")
        layout.addWidget(inp)
        
        list_widget = QListWidget()
        items = [
            "New Case", "Open Case", "Competition Dashboard", "Import Artifact", 
            "Quick Triage", "Decoder", "Forensics", "Steganography", 
            "Network", "Crypto", "Web", "Binary", "Memory", "Malware Static Triage", 
            "OSINT", "CTF Knowledge", "AI Copilot", "Tools", "Settings", 
            "Add Note", "Add Task", "Add Flag", "Generate Report"
        ]
        list_widget.addItems(items)
        layout.addWidget(list_widget)
        
        def filter_items(text):
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setHidden(text.lower() not in item.text().lower())
                
        inp.textChanged.connect(filter_items)
        
        def on_accept() -> None:
            curr = list_widget.currentItem()
            if curr:
                action = curr.text()
                dialog.accept()
                
                # Navigate if it's a sidebar item
                nav_map = {
                    "Competition Dashboard": "Competition Dashboard",
                    "Open Case": "Case Workspace",
                    "Quick Triage": "Quick Triage",
                    "Decoder": "Decoder",
                    "Forensics": "Forensics",
                    "Steganography": "Steganography",
                    "Network": "Network",
                    "Crypto": "Crypto",
                    "Web": "Web",
                    "Binary": "Binary",
                    "Memory": "Memory",
                    "Malware Static Triage": "Malware Static Triage",
                    "OSINT": "OSINT",
                    "AI Copilot": "AI Copilot",
                    "Tools": "Tools",
                    "Settings": "Settings",
                    "New Case": "New Case"
                }
                if action in nav_map:
                    self.navigate_to_item(nav_map[action])
                elif action in ["Import Artifact", "Add Note", "Add Task", "Add Flag", "Generate Report"]:
                    self.navigate_to_item("Case Workspace")
                    # Optionally trigger specific dialogs here if implemented in CaseWorkspaceView
            
        list_widget.itemDoubleClicked.connect(on_accept)
        dialog.exec()





