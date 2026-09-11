import logging
from typing import Any

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.artifact import Artifact
from app.models.case import Case
from app.services.artifact_service import artifact_service
from app.services.case_service import case_service
from app.services.triage_service import triage_service
from app.ui.workers import AnalysisWorker

logger = logging.getLogger(__name__)

class TriageView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_case: Case | None = None
        self.current_artifact: Artifact | None = None
        self.worker: AnalysisWorker | None = None
        self.init_ui()
        
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Controls
        control_layout = QHBoxLayout()
        self.btn_create_case = QPushButton("1. Create Test Case")
        self.btn_import = QPushButton("2. Import Artifact")
        self.btn_run = QPushButton("3. Run Triage")
        
        self.btn_import.setEnabled(False)
        self.btn_run.setEnabled(False)
        
        self.btn_create_case.clicked.connect(self.create_case)
        self.btn_import.clicked.connect(self.import_artifact)
        self.btn_run.clicked.connect(self.run_triage)
        
        control_layout.addWidget(self.btn_create_case)
        control_layout.addWidget(self.btn_import)
        control_layout.addWidget(self.btn_run)
        
        # Status
        self.lbl_status = QLabel("Ready")
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate initially hidden
        self.progress.setVisible(False)
        
        # Results area
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        self.txt_results.setStyleSheet("font-family: Consolas, monospace;")
        
        layout.addLayout(control_layout)
        layout.addWidget(self.lbl_status)
        layout.addWidget(self.progress)
        layout.addWidget(self.txt_results)
        
    def create_case(self) -> None:
        try:
            self.current_case = case_service.create_case("Triage_Test_Case", "Temporary case for triage testing.")
            if self.current_case:
                self.lbl_status.setText(f"Case Created: {self.current_case.id}")
                self.btn_import.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create case: {e}")
            
    def import_artifact(self) -> None:
        if not self.current_case:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Artifact to Import")
        if file_path:
            try:
                self.current_artifact = artifact_service.ingest_file(self.current_case.id, file_path)
                if self.current_artifact:
                    self.lbl_status.setText(f"Artifact Imported: {self.current_artifact.filename}")
                    self.btn_run.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import artifact: {e}")
                
    def run_triage(self) -> None:
        if not self.current_artifact:
            return
            
        self.btn_run.setEnabled(False)
        self.lbl_status.setText("Running Triage...")
        self.progress.setVisible(True)
        self.txt_results.clear()
        
        self.worker = AnalysisWorker(triage_service.run_triage, self.current_artifact)
        self.worker.finished.connect(self.on_triage_finished)
        self.worker.error.connect(self.on_triage_error)
        self.worker.start()
        
    def on_triage_finished(self, result: Any) -> None:
        self.progress.setVisible(False)
        self.btn_run.setEnabled(True)
        self.lbl_status.setText("Triage Completed")
        
        output = [
            f"--- TRIAGE RESULT FOR {result.artifact.filename} ---",
            f"Size: {result.artifact.size} bytes",
            f"Stored Path: {result.artifact.stored_path}",
            "",
            "--- HASHES ---",
            f"MD5: {result.hashes.get('md5')}",
            f"SHA256: {result.hashes.get('sha256')}",
            "",
            "--- FILE IDENTIFICATION ---"
        ]
        
        for k, v in result.file_identification.items():
            output.append(f"{k}: {v}")
            
        if result.entropy:
            output.extend([
                "",
                "--- ENTROPY ---",
                f"Shannon Entropy: {result.entropy.entropy:.4f}"
            ])
            
        output.append("\n--- EXTRACTED STRINGS (Sample) ---")
        for s in result.strings[:20]:
            output.append(f"0x{s.offset:04x} [{s.encoding}] {s.string}")
            
        output.append("\n--- FINDINGS ---")
        for f in result.findings:
            output.append(f"[{f.severity}] {f.title}: {f.description}")
            
        self.txt_results.setText("\n".join(output))
        
    def on_triage_error(self, err_msg: str) -> None:
        self.progress.setVisible(False)
        self.btn_run.setEnabled(True)
        self.lbl_status.setText("Triage Failed")
        QMessageBox.critical(self, "Triage Error", err_msg)

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
