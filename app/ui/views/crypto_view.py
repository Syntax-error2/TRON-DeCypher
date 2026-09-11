from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.crypto.analyzers.frequency import frequency_analysis_service
from app.crypto.classical.caesar import caesar_analyzer
from app.crypto.models import CryptoInput
from app.crypto.modern.hashes import hash_analysis_service
from app.crypto.rsa.assessment import rsa_assessment_service
from app.crypto.services.identification import crypto_identification_service
from app.crypto.xor.analyzer import xor_analyzer
from app.osint.extraction import ioc_extraction_service
from app.ui.views.knowledge_panel import KnowledgePanel


class CryptoView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # Tabs for Analytical domains
        self.tabs = QTabWidget()
        
        # 1. Classical / Generic Analysis Tab
        self.tab_general = QWidget()
        self.setup_general_tab()
        self.tabs.addTab(self.tab_general, "General Analysis")
        
        # 2. RSA Analysis Tab
        self.tab_rsa = QWidget()
        self.setup_rsa_tab()
        self.tabs.addTab(self.tab_rsa, "RSA Analysis")
        
        main_layout.addWidget(self.tabs)

        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("RSA AES Caesar Hash Cracking")
        main_layout.addWidget(self.kn_panel)

        
    def setup_general_tab(self) -> None:
        layout = QVBoxLayout(self.tab_general)
        
        # Input
        grp_input = QGroupBox("Ciphertext Input")
        inp_layout = QVBoxLayout(grp_input)
        self.txt_input = QTextEdit()
        inp_layout.addWidget(self.txt_input)
        
        btn_layout = QHBoxLayout()
        self.btn_identify = QPushButton("Identify")
        self.btn_freq = QPushButton("Frequency / IoC")
        self.btn_caesar = QPushButton("Caesar Crack")
        self.btn_xor = QPushButton("XOR 1-byte Crack")
        self.btn_hash = QPushButton("Identify Hash")
        
        btn_layout.addWidget(self.btn_identify)
        btn_layout.addWidget(self.btn_freq)
        btn_layout.addWidget(self.btn_caesar)
        btn_layout.addWidget(self.btn_xor)
        btn_layout.addWidget(self.btn_hash)
        
        self.btn_identify.clicked.connect(self.run_identify)
        self.btn_freq.clicked.connect(self.run_freq)
        self.btn_caesar.clicked.connect(self.run_caesar)
        self.btn_xor.clicked.connect(self.run_xor)
        self.btn_hash.clicked.connect(self.run_hash)
        
        inp_layout.addLayout(btn_layout)
        
        # Output
        grp_output = QGroupBox("Analysis Results")
        out_layout = QVBoxLayout(grp_output)
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        out_layout.addWidget(self.txt_output)
        
        actions_layout = QHBoxLayout()
        self.btn_extract_ioc = QPushButton("Extract IOCs from Result")
        self.btn_extract_ioc.clicked.connect(self.extract_iocs)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_extract_ioc)
        out_layout.addLayout(actions_layout)
        
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(grp_input)
        splitter.addWidget(grp_output)
        layout.addWidget(splitter)
        
    def setup_rsa_tab(self) -> None:
        layout = QVBoxLayout(self.tab_rsa)
        
        form_layout = QFormLayout()
        self.inp_n = QLineEdit()
        self.inp_e = QLineEdit()
        self.inp_c = QLineEdit()
        self.inp_p = QLineEdit()
        self.inp_q = QLineEdit()
        
        form_layout.addRow("n (Modulus):", self.inp_n)
        form_layout.addRow("e (Public Exp):", self.inp_e)
        form_layout.addRow("c (Ciphertext):", self.inp_c)
        form_layout.addRow("p (Prime 1):", self.inp_p)
        form_layout.addRow("q (Prime 2):", self.inp_q)
        
        btn_rsa_analyze = QPushButton("Assess RSA & Attempt Local Factorization")
        btn_rsa_analyze.clicked.connect(self.run_rsa)
        
        self.txt_rsa_out = QTextEdit()
        self.txt_rsa_out.setReadOnly(True)
        
        layout.addLayout(form_layout)
        layout.addWidget(btn_rsa_analyze)
        layout.addWidget(self.txt_rsa_out)
        
    # --- Action Handlers ---
    
    def run_identify(self) -> None:
        ci = CryptoInput(value=self.txt_input.toPlainText())
        res = crypto_identification_service.analyze(ci)
        out = "--- Detection Results ---\n"
        for c in res.candidates:
            out += f"{c['algorithm']}: {c['confidence']:.2f} ({c['reason']})\n"
        self.txt_output.setText(out)
        
    def run_freq(self) -> None:
        ci = CryptoInput(value=self.txt_input.toPlainText())
        res = frequency_analysis_service.analyze(ci)
        if not res.success:
            self.txt_output.setText(f"Error: {res.errors}")
            return
            
        out = f"Length: {res.parameters.get('length')}\n"
        out += f"IoC: {res.parameters.get('ioc', 0):.4f}\n\n"
        out += "Observations:\n" + "\n".join(res.observations) + "\n\n"
        
        freq = res.parameters.get("frequencies", {})
        sorted_freq = sorted(freq.items(), key=lambda item: item[1], reverse=True)
        out += "Frequencies:\n"
        for char, pct in sorted_freq:
            out += f"{char}: {pct:.2f}%\n"
            
        self.txt_output.setText(out)
        
    def run_caesar(self) -> None:
        ci = CryptoInput(value=self.txt_input.toPlainText())
        res = caesar_analyzer.analyze(ci)
        out = "--- Caesar Candidates ---\n"
        out += "\n".join(res.observations) + "\n\n"
        for c in res.candidates[:5]:
            out += f"Shift {c['shift']} (Score: {c['score']:.1f}): {c['preview']}\n"
        self.txt_output.setText(out)
        
    def run_xor(self) -> None:
        # For XOR we try to decode hex first if it looks like hex
        text = self.txt_input.toPlainText().strip()
        import re
        input_type = "hex" if re.match(r'^([0-9a-fA-F]{2})+$', text) else "text"
            
        ci = CryptoInput(value=text, input_type=input_type)
        res = xor_analyzer.analyze_single_byte(ci)
        
        out = "--- Single-Byte XOR Candidates ---\n"
        if not res.candidates:
            out += "No valid printable candidates found."
        else:
            for c in res.candidates[:10]:
                out += f"Key {c['key']} (Ratio: {c['printable_ratio']:.2f}): {c['preview']}\n"
        self.txt_output.setText(out)
        
    def run_hash(self) -> None:
        ci = CryptoInput(value=self.txt_input.toPlainText())
        res = hash_analysis_service.identify(ci)
        out = "--- Hash Candidates ---\n"
        for c in res.candidates:
            out += f"{c['algorithm']} ({c['confidence']:.2f})\n"
        self.txt_output.setText(out)
        
    def run_rsa(self) -> None:
        def parse_int(s: str) -> int | None:
            s = s.strip()
            if not s: return None
            try:
                return int(s, 16) if s.startswith("0x") else int(s)
            except Exception:
                return None
                
        n = parse_int(self.inp_n.text())
        e = parse_int(self.inp_e.text())
        c = parse_int(self.inp_c.text())
        p = parse_int(self.inp_p.text())
        q = parse_int(self.inp_q.text())
        
        self.txt_rsa_out.setText("Analyzing RSA parameters...")
        # Since bounded factorization is quick, we run synchronously in this prototype
        res = rsa_assessment_service.assess(n, e, c, p, q)
        
        out = "--- RSA Assessment ---\n"
        for obs in res.observations:
            out += f"- {obs}\n"
            
        out += "\n--- Recovered Parameters ---\n"
        for k, v in res.parameters.items():
            if k == "pt_int": continue
            out += f"{k}: {hex(v) if isinstance(v, int) else v}\n"
            
        self.txt_rsa_out.setText(out)
        
    def extract_iocs(self) -> None:
        text = self.txt_output.toPlainText()
        iocs = ioc_extraction_service.extract(text, case_id="temp_crypto_case")
        if iocs:
            QMessageBox.information(self, "IOCs", f"Extracted {len(iocs)} IOCs! Switch to OSINT view to see them.")
        else:
            QMessageBox.information(self, "IOCs", "No IOCs found in the analysis result.")

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
