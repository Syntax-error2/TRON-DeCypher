from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.reporting.services.reporting_service import ReportConfig, reporting_service
from app.services.artifact_service import artifact_service
from app.services.case_service import case_service


class CaseWorkspaceView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_case_id = ""
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        lbl_title = QLabel("<b>TRON-DeCypher — Case Workspace</b>")
        font = lbl_title.font()
        font.setPointSize(16)
        lbl_title.setFont(font)
        main_layout.addWidget(lbl_title)
        
        self.tabs = QTabWidget()
        
        # 1. Overview
        self.tab_overview = QWidget()
        ov_layout = QVBoxLayout(self.tab_overview)
        self.txt_overview = QTextEdit()
        self.txt_overview.setReadOnly(True)
        ov_layout.addWidget(self.txt_overview)
        self.tabs.addTab(self.tab_overview, "Overview")
        
        # 2. Evidence
        self.tab_evidence = QWidget()
        ev_layout = QVBoxLayout(self.tab_evidence)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.tree_evidence = QTreeWidget()
        self.tree_evidence.setHeaderLabels(["Artifact", "Size", "MIME"])
        self.tree_evidence.itemSelectionChanged.connect(self.on_evidence_selected)
        
        self.panel_evidence_detail = QTextEdit()
        self.panel_evidence_detail.setReadOnly(True)
        
        splitter.addWidget(self.tree_evidence)
        splitter.addWidget(self.panel_evidence_detail)
        splitter.setSizes([300, 500])
        ev_layout.addWidget(splitter)
        self.tabs.addTab(self.tab_evidence, "Evidence")
        
        # 3. Findings
        self.tab_findings = QTableWidget()
        self.tab_findings.setColumnCount(3)
        self.tab_findings.setHorizontalHeaderLabels(["Severity", "Title", "Description"])
        self.tabs.addTab(self.tab_findings, "Findings")
        
        # 4. IOCs
        self.tab_iocs = QTableWidget()
        self.tab_iocs.setColumnCount(3)
        self.tab_iocs.setHorizontalHeaderLabels(["Type", "Value", "Context"])

        self.tabs.addTab(self.tab_iocs, "IOCs")
        
        # 4a. Flags
        self.tab_flags = QWidget()
        flag_layout = QVBoxLayout(self.tab_flags)
        
        self.table_flags = QTableWidget()
        self.table_flags.setColumnCount(4)
        self.table_flags.setHorizontalHeaderLabels(["ID", "Flag", "Status", "Actions"])
        
        btn_add_flag = QPushButton("Add Flag")
        btn_add_flag.clicked.connect(self.prompt_add_flag)
        
        flag_layout.addWidget(self.table_flags)
        flag_layout.addWidget(btn_add_flag)
        self.tabs.addTab(self.tab_flags, "Flags")
        
        # 4b. Tasks
        self.tab_tasks = QWidget()
        task_layout = QVBoxLayout(self.tab_tasks)
        
        self.table_tasks = QTableWidget()
        self.table_tasks.setColumnCount(4)
        self.table_tasks.setHorizontalHeaderLabels(["Title", "Status", "Priority", "Actions"])
        
        btn_add_task = QPushButton("Add Task")
        btn_add_task.clicked.connect(self.prompt_add_task)
        
        task_layout.addWidget(self.table_tasks)
        task_layout.addWidget(btn_add_task)
        self.tabs.addTab(self.tab_tasks, "Tasks")
        
        # 5. Reports

        
        # 5. Reports
        self.tab_reports = QWidget()
        rep_layout = QVBoxLayout(self.tab_reports)
        rep_layout.addWidget(QLabel("Generate Case Reports"))
        btn_json = QPushButton("Export JSON Report")
        btn_json.clicked.connect(lambda: self.generate_report("json", "JSON Files (*.json)"))
        btn_csv = QPushButton("Export CSV Report")
        btn_csv.clicked.connect(lambda: self.generate_report("csv", "CSV Files (*.csv)"))
        btn_pdf = QPushButton("Export PDF Report")
        btn_pdf.clicked.connect(lambda: self.generate_report("pdf", "PDF Files (*.pdf)"))
        rep_layout.addWidget(btn_json)
        rep_layout.addWidget(btn_csv)
        rep_layout.addWidget(btn_pdf)
        rep_layout.addStretch()
        self.tabs.addTab(self.tab_reports, "Reporting")
        
        main_layout.addWidget(self.tabs)
        
    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
        self.refresh_case_data()

    def refresh_case_data(self) -> None:
        if not self.current_case_id:
            self.txt_overview.setText("No case selected.")
            self.tree_evidence.clear()
            self.tab_findings.setRowCount(0)
            self.tab_iocs.setRowCount(0)
            return

        case_obj = case_service.get_case(self.current_case_id)
        if not case_obj:
            return
            
        self.current_artifacts = artifact_service.get_all_artifacts(self.current_case_id)

        # Overview
        ov = f"Case ID: {case_obj.id}\n"
        ov += f"Name: {case_obj.name}\n"
        ov += f"Created: {case_obj.created_at}\n"
        ov += f"Artifact Count: {len(self.current_artifacts)}\n"
        self.txt_overview.setText(ov)

        # Evidence Tree
        self.tree_evidence.clear()
        for artifact in self.current_artifacts:
            item = QTreeWidgetItem([artifact.filename, str(artifact.size), artifact.mime_type])
            item.setData(0, Qt.ItemDataRole.UserRole, artifact)
            self.tree_evidence.addTopLevelItem(item)
        # Refresh Flags
        from PySide6.QtWidgets import QHBoxLayout, QTableWidgetItem, QWidget

        from app.database.database import db
        with db.get_connection() as conn:
            flags = conn.execute("SELECT id, flag_value, status FROM flags WHERE case_id = ?", (self.current_case_id,)).fetchall()
            self.table_flags.setRowCount(len(flags))
            for i, row in enumerate(flags):
                self.table_flags.setItem(i, 0, QTableWidgetItem(row['id']))
                self.table_flags.setItem(i, 1, QTableWidgetItem(row['flag_value']))
                self.table_flags.setItem(i, 2, QTableWidgetItem(row['status']))
                
                actions = QWidget()
                l = QHBoxLayout(actions)
                l.setContentsMargins(0,0,0,0)
                
                btn_c = QPushButton("Confirm")
                btn_c.clicked.connect(lambda _, fid=row['id']: self.update_flag_status(fid, "CONFIRMED"))
                btn_r = QPushButton("Reject")
                btn_r.clicked.connect(lambda _, fid=row['id']: self.update_flag_status(fid, "REJECTED"))
                
                l.addWidget(btn_c)
                l.addWidget(btn_r)
                self.table_flags.setCellWidget(i, 3, actions)
                
        # Refresh Tasks
        with db.get_connection() as conn:
            tasks = conn.execute("SELECT id, title, status, priority FROM case_tasks WHERE case_id = ?", (self.current_case_id,)).fetchall()
            self.table_tasks.setRowCount(len(tasks))
            for i, row in enumerate(tasks):
                self.table_tasks.setItem(i, 0, QTableWidgetItem(row['title']))
                self.table_tasks.setItem(i, 1, QTableWidgetItem(row['status']))
                self.table_tasks.setItem(i, 2, QTableWidgetItem(row['priority']))
                
                actions = QWidget()
                l = QHBoxLayout(actions)
                l.setContentsMargins(0,0,0,0)
                
                btn_d = QPushButton("Done")
                btn_d.clicked.connect(lambda _, tid=row['id']: self.update_task_status(tid, "DONE"))
                btn_r = QPushButton("Reopen")
                btn_r.clicked.connect(lambda _, tid=row['id']: self.update_task_status(tid, "TODO"))
                
                l.addWidget(btn_d)
                l.addWidget(btn_r)
                self.table_tasks.setCellWidget(i, 3, actions)

            
    def on_evidence_selected(self) -> None:
        selected = self.tree_evidence.selectedItems()
        if not selected:
            self.panel_evidence_detail.clear()
            return
            
        item = selected[0]
        artifact = item.data(0, Qt.ItemDataRole.UserRole)
        
        details = f"Filename: {artifact.filename}\n"
        details += f"Path: {artifact.path}\n"
        details += f"Size: {artifact.size} bytes\n"
        details += f"MIME: {artifact.mime_type}\n"
        details += f"MD5: {artifact.md5}\n"
        details += f"SHA256: {artifact.sha256}\n"
        
        self.panel_evidence_detail.setText(details)

    def generate_report(self, fmt: str, ext_filter: str) -> None:
        if not self.current_case_id:
            QMessageBox.warning(self, "No Case", "Please select or create a case first.")
            return
            
        path, _ = QFileDialog.getSaveFileName(self, f"Save {fmt.upper()} Report", "", ext_filter)
        if not path:
            return
            
        config = ReportConfig(
            case_id=self.current_case_id,
            export_path=path,
            format_type=fmt
        )
        
        success = reporting_service.generate_report(config)
        
        if success:
            QMessageBox.information(self, "Export Complete", f"Report saved to {path}")
        else:
            QMessageBox.critical(self, "Export Failed", "There was an error generating the report.")




    def prompt_add_flag(self):
        if not self.current_case_id:
            return
        from PySide6.QtWidgets import QInputDialog
        flag, ok = QInputDialog.getText(self, "Add Flag", "Enter Flag:")
        if ok and flag:
            import time
            import uuid

            from app.database.database import db
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO flags (id, case_id, flag_value, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (f"flag_{uuid.uuid4().hex[:8]}", self.current_case_id, flag, "CANDIDATE", time.time(), time.time())
                )
            self.refresh_case_data()
            
    def prompt_add_task(self):
        if not self.current_case_id:
            return
        from PySide6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, "Add Task", "Task Title:")
        if ok and title:
            import time
            import uuid

            from app.database.database import db
            with db.get_connection() as conn:
                conn.execute(
                    "INSERT INTO case_tasks (id, case_id, title, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (f"task_{uuid.uuid4().hex[:8]}", self.current_case_id, title, "TODO", "MEDIUM", time.time(), time.time())
                )
            self.refresh_case_data()
            
    def update_flag_status(self, flag_id, status):
        from app.database.database import db
        with db.get_connection() as conn:
            conn.execute("UPDATE flags SET status = ? WHERE id = ?", (status, flag_id))
        self.refresh_case_data()

    def update_task_status(self, task_id, status):
        from app.database.database import db
        with db.get_connection() as conn:
            conn.execute("UPDATE case_tasks SET status = ? WHERE id = ?", (status, task_id))
        self.refresh_case_data()
