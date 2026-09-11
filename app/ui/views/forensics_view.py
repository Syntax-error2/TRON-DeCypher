from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.forensics.analyzers.embedded import EmbeddedDataAnalyzer
from app.forensics.analyzers.metadata import MetadataAnalyzer
from app.forensics.analyzers.signature import FileSignatureAnalyzer
from app.forensics.services.archive_service import archive_service
from app.models.artifact import Artifact
from app.ui.views.knowledge_panel import KnowledgePanel
from app.ui.widgets.hex_viewer import HexViewer


class ForensicsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_artifact: Artifact | None = None
        self.metadata_analyzer = MetadataAnalyzer()
        self.signature_analyzer = FileSignatureAnalyzer()
        self.embedded_analyzer = EmbeddedDataAnalyzer()
        
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self.lbl_artifact = QLabel("Artifact: None")
        self.btn_analyze = QPushButton("Analyze")
        self.btn_extract_ioc = QPushButton("Extract IOCs")
        self.btn_extract_ioc.clicked.connect(self.extract_iocs)
        self.btn_analyze.clicked.connect(self.run_analysis)
        header.addWidget(self.lbl_artifact)
        header.addStretch()
        header.addWidget(self.btn_extract_ioc)
        header.addWidget(self.btn_analyze)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab: Overview
        self.tab_overview = QWidget()
        overview_layout = QVBoxLayout(self.tab_overview)
        
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        
        self.tree_structure = QTreeWidget()
        self.tree_structure.setHeaderLabels(["Structure / Findings", "Offset / Details"])
        
        overview_layout.addWidget(QLabel("Summary & Metadata"))
        overview_layout.addWidget(self.txt_summary)
        overview_layout.addWidget(QLabel("File Structure & Findings"))
        overview_layout.addWidget(self.tree_structure)
        
        self.tabs.addTab(self.tab_overview, "Overview")
        
        # Tab: Hex View
        self.tab_hex = HexViewer()
        self.tabs.addTab(self.tab_hex, "Hex Viewer")
        
        main_layout.addLayout(header)
        main_layout.addWidget(self.tabs)

        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("Metadata File Headers Carving")
        main_layout.addWidget(self.kn_panel)

        
    def load_artifact(self, artifact: Artifact) -> None:
        self.current_artifact = artifact
        self.lbl_artifact.setText(f"Artifact: {artifact.filename}")
        self.tab_hex.load_file(Path(artifact.stored_path))
        self.run_analysis()
        
    def run_analysis(self) -> None:
        if not self.current_artifact:
            return
            
        file_path = Path(self.current_artifact.stored_path)
        if not file_path.exists():
            QMessageBox.critical(self, "Error", "Artifact file missing.")
            return
            
        # 1. Metadata
        meta = self.metadata_analyzer.analyze(file_path)
        summary = f"Filename: {meta.get('filename')}\n"
        summary += f"Size: {meta.get('size')} bytes\n"
        summary += f"MIME: {meta.get('mime_type')}\n"
        if "image" in meta:
            summary += f"Image Format: {meta['image'].get('format')} {meta['image'].get('width')}x{meta['image'].get('height')}\n"
        self.txt_summary.setText(summary)
        
        # 2. Signatures
        self.tree_structure.clear()
        
        sig_root = QTreeWidgetItem(self.tree_structure, ["Signatures"])
        matches = self.signature_analyzer.analyze(file_path)
        for m in matches:
            item = QTreeWidgetItem(sig_root, [m.detected_type, f"0x{m.offset:X} - {m.description}"])
            
        mismatch = self.signature_analyzer.check_mismatch(self.current_artifact.filename, matches)
        if mismatch:
            finding = QTreeWidgetItem(self.tree_structure, ["⚠️ Mismatch", mismatch])
            finding.setForeground(0, Qt.GlobalColor.red)
            
        # 3. Embedded Data
        embed_root = QTreeWidgetItem(self.tree_structure, ["Embedded Data"])
        embedded = self.embedded_analyzer.analyze_embedded_signatures(file_path)
        for e in embedded:
            item = QTreeWidgetItem(embed_root, [e.detected_type, f"0x{e.offset:X}"])
            
        # EOF Appended
        appended_offset = None
        if matches:
            appended_offset = self.embedded_analyzer.check_appended_data(file_path, matches[0].detected_type)
        if appended_offset:
            item = QTreeWidgetItem(self.tree_structure, ["⚠️ Appended Data", f"0x{appended_offset:X}"])
            item.setForeground(0, Qt.GlobalColor.red)
            
        # 4. ZIP Inspection
        if matches and any(m.detected_type == "ZIP" for m in matches):
            zip_root = QTreeWidgetItem(self.tree_structure, ["ZIP Contents"])
            contents = archive_service.inspect_zip(file_path)
            for c in contents:
                QTreeWidgetItem(zip_root, [c['filename'], f"{c['size']} bytes"])
                
        self.tree_structure.expandAll()
    def extract_iocs(self) -> None:
        if not self.current_artifact:
            return
        from app.osint.extraction import ioc_extraction_service
        text = self.txt_summary.toPlainText()
        # In a real app we'd also scan the HexViewer output or file contents directly.
        iocs = ioc_extraction_service.extract(text, case_id=self.current_artifact.case_id)
        from PySide6.QtWidgets import QMessageBox
        if iocs:
            QMessageBox.information(self, "IOCs Extracted", f"Found {len(iocs)} indicators of compromise in summary.")
        else:
            QMessageBox.information(self, "IOCs Extracted", "No IOCs found in summary.")

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
