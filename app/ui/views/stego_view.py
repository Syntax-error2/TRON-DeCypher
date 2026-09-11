from pathlib import Path

from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.models.artifact import Artifact
from app.stego.analyzers.lsb import LSBAnalyzer
from app.ui.views.knowledge_panel import KnowledgePanel


class StegoView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_artifact: Artifact | None = None
        self.lsb_analyzer = LSBAnalyzer()
        
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        self.lbl_artifact = QLabel("Artifact: None")
        self.btn_analyze = QPushButton("Run Steganography Scan")
        self.btn_analyze.clicked.connect(self.run_analysis)
        header.addWidget(self.lbl_artifact)
        header.addStretch()
        header.addWidget(self.btn_analyze)
        
        # Results
        results_group = QGroupBox("LSB Analysis Results")
        results_layout = QVBoxLayout(results_group)
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        results_layout.addWidget(self.txt_results)
        
        self.btn_send_decoder = QPushButton("Send Selected to Decoder")
        self.btn_extract_ioc = QPushButton("Extract IOCs")
        self.btn_extract_ioc.clicked.connect(self.extract_iocs)
        results_layout.addWidget(self.btn_send_decoder)
        results_layout.addWidget(self.btn_extract_ioc)
        
        main_layout.addLayout(header)
        main_layout.addWidget(results_group)

        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("Steganography LSB bitplane")
        main_layout.addWidget(self.kn_panel)

        
    def load_artifact(self, artifact: Artifact) -> None:
        self.current_artifact = artifact
        self.lbl_artifact.setText(f"Artifact: {artifact.filename}")
        self.txt_results.clear()
        
    def run_analysis(self) -> None:
        if not self.current_artifact:
            return
            
        file_path = Path(self.current_artifact.stored_path)
        if not file_path.exists():
            QMessageBox.critical(self, "Error", "Artifact file missing.")
            return
            
        self.txt_results.setText("Analyzing LSB...\n")
        
        results = self.lsb_analyzer.analyze(file_path)
        
        if not results:
            self.txt_results.append("No obvious textual LSB steganography detected.")
            return
            
        for r in results:
            self.txt_results.append(f"--- Channel: {r.channel} ---")
            self.txt_results.append(f"Printable ratio: {r.metadata.get('printable_ratio', 0):.2f}")
            self.txt_results.append(f"Text Preview:\n{r.extracted_text}\n")
    def extract_iocs(self) -> None:
        if not self.current_artifact:
            return
        from app.osint.extraction import ioc_extraction_service
        text = self.txt_results.toPlainText()
        iocs = ioc_extraction_service.extract(text, case_id=self.current_artifact.case_id)
        from PySide6.QtWidgets import QMessageBox
        if iocs:
            QMessageBox.information(self, "IOCs Extracted", f"Found {len(iocs)} indicators of compromise in stego results.")
        else:
            QMessageBox.information(self, "IOCs Extracted", "No IOCs found.")

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
