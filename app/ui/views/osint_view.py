import json

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.osint.enrichment import ioc_enrichment_service
from app.osint.models import IOC


class OsintView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.iocs: list[IOC] = []
        self.init_ui()
        
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("IOC Intelligence & Threat Intel (OSINT)"))
        header.addStretch()
        
        self.chk_offline = QCheckBox("Offline Mode (Safe)")
        self.chk_offline.setChecked(True)
        self.chk_offline.stateChanged.connect(self.toggle_offline)
        header.addWidget(self.chk_offline)
        
        self.btn_export = QPushButton("Export JSON")
        self.btn_export.clicked.connect(self.export_iocs)
        header.addWidget(self.btn_export)
        
        # Table of IOCs
        self.tree_iocs = QTreeWidget()
        self.tree_iocs.setHeaderLabels(["IOC Value", "Type", "Normalized", "Status"])
        self.tree_iocs.itemClicked.connect(self.ioc_selected)
        
        # Detail Panel
        detail_group = QGroupBox("IOC Details & Enrichment")
        detail_layout = QVBoxLayout(detail_group)
        
        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        
        btn_layout = QHBoxLayout()
        self.btn_enrich = QPushButton("Enrich Selected")
        self.btn_enrich.setEnabled(False)
        self.btn_enrich.clicked.connect(self.enrich_selected)
        btn_layout.addWidget(self.btn_enrich)
        btn_layout.addStretch()
        
        detail_layout.addWidget(self.txt_details)
        detail_layout.addLayout(btn_layout)
        
        layout.addLayout(header)
        layout.addWidget(self.tree_iocs, stretch=2)
        layout.addWidget(detail_group, stretch=1)
        
    def toggle_offline(self, state: int) -> None:
        ioc_enrichment_service.offline_mode = (state != 0)
        
    def add_iocs(self, iocs: list[IOC]) -> None:
        self.iocs.extend(iocs)
        for ioc in iocs:
            item = QTreeWidgetItem(self.tree_iocs, [
                ioc.value,
                ioc.ioc_type.value,
                ioc.normalized_value,
                "Local"
            ])
            item.setData(0, 32, ioc)
            
    def ioc_selected(self, item: QTreeWidgetItem, column: int) -> None:
        ioc: IOC = item.data(0, 32)
        if not ioc:
            return
            
        self.btn_enrich.setEnabled(True)
        
        details = f"Type: {ioc.ioc_type.value}\n"
        details += f"Original: {ioc.value}\n"
        details += f"Normalized: {ioc.normalized_value}\n\n"
        details += "--- Enrichment Results ---\n"
        
        if not ioc.intel_results:
            details += "No enrichment data.\n"
        else:
            for r in ioc.intel_results:
                details += f"[{r.provider}] {r.response_summary}\n"
                
        self.txt_details.setText(details)
        
    def enrich_selected(self) -> None:
        item = self.tree_iocs.currentItem()
        if not item:
            return
            
        ioc: IOC = item.data(0, 32)
        if not ioc:
            return
            
        self.txt_details.append("\nQuerying providers...\n")
        results = ioc_enrichment_service.enrich_ioc(ioc)
        
        if results:
            ioc.intel_results.extend(results)
            for r in results:
                self.txt_details.append(f"[{r.provider}] {r.response_summary}")
            item.setText(3, "Enriched (Cached/Stub)")
        else:
            self.txt_details.append("No results found.")
            item.setText(3, "No Data")
            
    def export_iocs(self) -> None:
        if not self.iocs:
            QMessageBox.warning(self, "Export", "No IOCs to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export IOCs", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        export_data = []
        for ioc in self.iocs:
            export_data.append({
                "type": ioc.ioc_type.value,
                "value": ioc.value,
                "normalized_value": ioc.normalized_value,
                "intel_count": len(ioc.intel_results)
            })
            
        try:
            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)
            QMessageBox.information(self, "Export", "Successfully exported IOCs.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
