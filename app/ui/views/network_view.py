from PySide6.QtWidgets import (
    QFileDialog,
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

from app.models.artifact import Artifact
from app.network.analyzers.orchestrator import network_orchestrator
from app.network.models import PcapStatistics
from app.network.services.ioc_integration import network_ioc_integration
from app.ui.views.knowledge_panel import KnowledgePanel


class NetworkView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_stats: PcapStatistics | None = None
        self.current_artifact: Artifact | None = None
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self.lbl_artifact = QLabel("PCAP: None")
        header.addWidget(self.lbl_artifact)
        
        self.btn_open = QPushButton("Open PCAP")
        self.btn_analyze = QPushButton("Analyze")
        self.btn_extract_ioc = QPushButton("Extract IOCs")
        
        self.btn_open.clicked.connect(self.open_pcap)
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_extract_ioc.clicked.connect(self.extract_iocs)
        
        header.addStretch()
        header.addWidget(self.btn_open)
        header.addWidget(self.btn_analyze)
        header.addWidget(self.btn_extract_ioc)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab: Summary
        self.tab_summary = QWidget()
        summary_layout = QVBoxLayout(self.tab_summary)
        self.txt_summary = QTextEdit()
        self.txt_summary.setReadOnly(True)
        summary_layout.addWidget(self.txt_summary)
        self.tabs.addTab(self.tab_summary, "Summary")
        
        # Tab: Conversations
        self.tab_convos = QWidget()
        convos_layout = QVBoxLayout(self.tab_convos)
        self.tree_convos = QTreeWidget()
        self.tree_convos.setHeaderLabels(["Source", "Destination", "Protocol", "Packets", "Bytes"])
        convos_layout.addWidget(self.tree_convos)
        self.tabs.addTab(self.tab_convos, "Conversations")
        
        # Tab: DNS
        self.tab_dns = QWidget()
        dns_layout = QVBoxLayout(self.tab_dns)
        self.tree_dns = QTreeWidget()
        self.tree_dns.setHeaderLabels(["Time", "Client", "Query", "Type", "Answers"])
        dns_layout.addWidget(self.tree_dns)
        self.tabs.addTab(self.tab_dns, "DNS")
        
        # Tab: HTTP
        self.tab_http = QWidget()
        http_layout = QVBoxLayout(self.tab_http)
        self.tree_http = QTreeWidget()
        self.tree_http.setHeaderLabels(["Time", "Client", "Method", "Host", "URI"])
        http_layout.addWidget(self.tree_http)
        self.tabs.addTab(self.tab_http, "HTTP")
        
        main_layout.addLayout(header)
        main_layout.addWidget(self.tabs)

        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("PCAP Wireshark")
        main_layout.addWidget(self.kn_panel)

        
    def open_pcap(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PCAP", "", "PCAP Files (*.pcap *.pcapng)")
        if file_path:
            self.lbl_artifact.setText(f"PCAP: {file_path}")
            # Mock artifact since we bypass triage selection in this standalone view
            self.current_artifact = Artifact(
                id="temp", case_id="temp_case", filename=file_path, original_path=file_path, stored_path=file_path, size=0
            )
            
    def run_analysis(self) -> None:
        if not self.current_artifact:
            QMessageBox.warning(self, "Error", "No PCAP selected.")
            return
            
        self.txt_summary.setText("Analyzing... (Streaming PCAP)")
        # In real app this would be in a QThread/Worker to avoid GUI freeze
        self.current_stats = network_orchestrator.analyze_pcap(self.current_artifact.stored_path)
        self.update_ui_with_stats()
        
    def update_ui_with_stats(self) -> None:
        if not self.current_stats:
            return
            
        # Summary
        s = f"Total Packets: {self.current_stats.total_packets}\n"
        s += f"Total Bytes: {self.current_stats.total_bytes}\n"
        duration = self.current_stats.last_timestamp - self.current_stats.first_timestamp
        s += f"Duration: {duration:.2f} seconds\n\n"
        
        s += "--- Protocols ---\n"
        for proto, count in self.current_stats.protocols.items():
            s += f"{proto}: {count}\n"
            
        self.txt_summary.setText(s)
        
        # Convos
        self.tree_convos.clear()
        for c in self.current_stats.conversations:
            QTreeWidgetItem(self.tree_convos, [
                c.src_ip, c.dst_ip, c.protocol, str(c.packet_count), str(c.bytes_transferred)
            ])
            
        # DNS
        self.tree_dns.clear()
        for d in self.current_stats.dns_queries:
            QTreeWidgetItem(self.tree_dns, [
                str(d.timestamp), d.client, d.query, d.qtype, ", ".join(d.answers)
            ])
            
        # HTTP
        self.tree_http.clear()
        for h in self.current_stats.http_requests:
            QTreeWidgetItem(self.tree_http, [
                str(h.timestamp), h.client, h.method, h.host, h.uri
            ])
            
    def extract_iocs(self) -> None:
        if not self.current_stats:
            QMessageBox.warning(self, "Error", "Analyze PCAP first.")
            return
            
        iocs = network_ioc_integration.extract_from_stats(self.current_stats, "temp_case")
        if iocs:
            QMessageBox.information(self, "IOCs", f"Extracted {len(iocs)} IOCs from PCAP to OSINT view.")
        else:
            QMessageBox.information(self, "IOCs", "No IOCs found.")

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
