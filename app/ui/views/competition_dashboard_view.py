from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.competition_service import competition_service
from app.services.case_service import case_service


class NewCompetitionCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Competition Case")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        self.inp_name = QLineEdit()
        self.inp_category = QComboBox()
        self.inp_category.addItems(["Cryptography", "Web", "Forensics", "Steganography", "Reverse Engineering", "OSINT", "Miscellaneous"])
        self.inp_desc = QLineEdit()
        self.inp_time_limit = QLineEdit()
        self.inp_time_limit.setPlaceholderText("Optional (e.g. 120 for 120 minutes)")
        
        layout.addRow("Challenge Name:", self.inp_name)
        layout.addRow("Category:", self.inp_category)
        layout.addRow("Description:", self.inp_desc)
        layout.addRow("Time Limit (min):", self.inp_time_limit)
        
        self.btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        layout.addRow(self.btns)

class CompetitionDashboardView(QWidget):
    navigate_requested = Signal(str)
    case_activated = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.current_case_id = "" 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lbl_title = QLabel("<b>TRON-DeCypher - Competition Mode</b>")
        font = lbl_title.font()
        font.setPointSize(16)
        lbl_title.setFont(font)
        main_layout.addWidget(lbl_title)
        
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # --- Empty State ---
        self.empty_widget = QWidget()
        empty_layout = QVBoxLayout(self.empty_widget)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_empty = QLabel("NO ACTIVE COMPETITION CASE")
        lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_new_case = QPushButton("Create Competition Case")
        btn_new_case.setMinimumHeight(40)
        btn_new_case.clicked.connect(self.show_new_case_dialog)
        
        btn_open_case = QPushButton("Open Case")
        btn_open_case.setMinimumHeight(40)
        btn_open_case.clicked.connect(lambda: self.navigate_requested.emit("Case Workspace"))
        
        empty_layout.addWidget(lbl_empty)
        empty_layout.addWidget(btn_new_case)
        empty_layout.addWidget(btn_open_case)
        self.stack.addWidget(self.empty_widget)
        
        # --- Active State ---
        self.active_widget = QWidget()
        active_layout = QVBoxLayout(self.active_widget)
        
        # Active Case Info
        self.lbl_active_case = QLabel("Active Case: None")
        active_layout.addWidget(self.lbl_active_case)
        
        # Time Panel
        time_frame = QFrame()
        time_frame.setFrameShape(QFrame.Shape.StyledPanel)
        time_layout = QVBoxLayout(time_frame)
        
        self.lbl_time = QLabel("00:00:00")
        time_font = self.lbl_time.font()
        time_font.setPointSize(24)
        time_font.setBold(True)
        self.lbl_time.setFont(time_font)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status = QLabel("STATUS: STOPPED")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        from app.core.config import settings
        self.lbl_flag_format = QLabel(f"<b>Flag Format:</b> {settings.flag_pattern}")
        self.lbl_flag_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_timer)
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_timer)
        self.btn_resume = QPushButton("Resume")
        self.btn_resume.clicked.connect(self.start_timer)
        self.btn_reset = QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset_timer)
        
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_resume)
        btn_layout.addWidget(self.btn_reset)
        
        time_layout.addWidget(self.lbl_time)
        time_layout.addWidget(self.lbl_status)
        time_layout.addLayout(btn_layout)
        active_layout.addWidget(time_frame)
        
        # Progress Metrics
        prog_frame = QFrame()
        prog_frame.setFrameShape(QFrame.Shape.StyledPanel)
        prog_layout = QGridLayout(prog_frame)
        
        self.metric_labels = {}
        metrics = ["Artifacts", "Findings", "IOCs", "Flags", "Tasks", "Notes"]
        
        for i, m in enumerate(metrics):
            prog_layout.addWidget(QLabel(f"<b>{m}:</b>"), i // 3, (i % 3) * 2)
            lbl_val = QLabel("0")
            self.metric_labels[m.lower()] = lbl_val
            prog_layout.addWidget(lbl_val, i // 3, (i % 3) * 2 + 1)
            
        active_layout.addWidget(prog_frame)
        
        # Quick Capture
        qc_frame = QFrame()
        qc_frame.setFrameShape(QFrame.Shape.StyledPanel)
        qc_layout = QHBoxLayout(qc_frame)
        self.inp_qc = QLineEdit()
        self.inp_qc.setPlaceholderText("Quick Observation...")
        btn_qc = QPushButton("Capture")
        btn_qc.clicked.connect(self.quick_capture)
        qc_layout.addWidget(self.inp_qc)
        qc_layout.addWidget(btn_qc)
        active_layout.addWidget(QLabel("<b>Quick Capture</b>"))
        active_layout.addWidget(qc_frame)
        
        # Quick Actions
        qa_frame = QFrame()
        qa_frame.setFrameShape(QFrame.Shape.StyledPanel)
        qa_layout = QGridLayout(qa_frame)
        
        actions = [
            ("Import Artifact", "Import Artifact"),
            ("Quick Triage", "Malware Static Triage"),
            ("Decoder", "Decoder"),
            ("Forensics", "Forensics"),
            ("Stego", "Stego LSB"),
            ("Network", "Network"),
            ("Crypto", "Crypto"),
            ("Web", "Web"),
            ("Binary", "Binary"),
            ("Memory", "Memory"),
            ("OSINT", "OSINT"),
            ("AI Copilot", "AI Copilot")
        ]
        
        for i, (label, target) in enumerate(actions):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked=False, t=target: self.navigate_requested.emit(t))
            qa_layout.addWidget(btn, i // 4, i % 4)
            
        active_layout.addWidget(QLabel("<b>Quick Actions</b>"))
        active_layout.addWidget(qa_frame)
        

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

        self.stack.setCurrentIndex(0)
        
    def show_new_case_dialog(self):
        dlg = NewCompetitionCaseDialog(self)
        if dlg.exec():
            name = dlg.inp_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Challenge Name is required.")
                return
                
            category = dlg.inp_category.currentText()
            desc = dlg.inp_desc.text().strip()
            time_limit = dlg.inp_time_limit.text().strip()
            
            case = case_service.create_case(name, desc)
            
            from app.database.database import db
            with db.get_connection() as conn:
                conn.execute(
                    "UPDATE cases SET challenge_category = ? WHERE id = ?",
                    (category, case.id)
                )
            
            self.set_case(case.id)
            self.case_activated.emit(case.id)
        
    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
        if case_id:
            self.stack.setCurrentIndex(1)
            case = case_service.get_case(case_id)
            if case:
                self.lbl_active_case.setText(f"<b>ACTIVE CASE:</b> {case.name} ({case.id})")
            else:
                self.lbl_active_case.setText(f"<b>ACTIVE CASE:</b> {case_id}")
            self.refresh_metrics()
            self.update_timer_display()
            self.timer.start(1000)
        else:
            self.stack.setCurrentIndex(0)
            self.timer.stop()
        
    def start_timer(self) -> None:
        if self.current_case_id:
            competition_service.start_timer(self.current_case_id)
            self.update_timer_display()
            
    def pause_timer(self) -> None:
        if self.current_case_id:
            competition_service.pause_timer(self.current_case_id)
            self.update_timer_display()
            
    def reset_timer(self) -> None:
        if self.current_case_id:
            competition_service.reset_timer(self.current_case_id)
            self.update_timer_display()
            
    def update_timer_display(self) -> None:
        if not self.current_case_id:
            return
            
        state = competition_service.get_timer_state(self.current_case_id)
        
        elapsed_sec = int(state["elapsed"])
        h = elapsed_sec // 3600
        m = (elapsed_sec % 3600) // 60
        s = elapsed_sec % 60
        
        self.lbl_time.setText(f"{h:02d}:{m:02d}:{s:02d}")
        
        if state["running"]:
            self.lbl_status.setText("STATUS: IN PROGRESS")
            self.lbl_status.setStyleSheet("color: #4CAF50;")
            self.btn_start.setVisible(False)
            self.btn_resume.setVisible(False)
            self.btn_pause.setVisible(True)
        else:
            if elapsed_sec > 0:
                self.lbl_status.setText("STATUS: PAUSED")
                self.btn_start.setVisible(False)
                self.btn_resume.setVisible(True)
                self.btn_pause.setVisible(False)
            else:
                self.lbl_status.setText("STATUS: NOT STARTED")
                self.btn_start.setVisible(True)
                self.btn_resume.setVisible(False)
                self.btn_pause.setVisible(False)
            self.lbl_status.setStyleSheet("color: #F44336;")
            
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
                
    def quick_capture(self) -> None:
        if not self.current_case_id:
            return
        note = self.inp_qc.text().strip()
        if note:
            import time
            import uuid

            from app.database.database import db
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO case_notes (id, case_id, title, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (f"note_{uuid.uuid4().hex[:8]}", self.current_case_id, "Quick Observation", note, time.time(), time.time())
                )
            self.inp_qc.clear()
            self.refresh_metrics()
            QMessageBox.information(self, "Success", "Note captured.")
