from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.osint.extraction import ioc_extraction_service
from app.ui.views.knowledge_panel import KnowledgePanel
from app.web.clients.httpx_client import safe_http_client
from app.web.models import HTTPRequest, HTTPResponse
from app.web.parsers.http_parser import raw_http_parser
from app.web.services.web_analysis_service import web_analysis_service


class WebView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        # By default, keep offline mode on
        safe_http_client.offline_mode = True
        self.current_response: HTTPResponse | None = None
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # Splitter: Request Builder (Top), Analysis/Response (Bottom)
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # --- TOP: Request Builder ---
        grp_request = QGroupBox("Request Builder / Target")
        req_layout = QVBoxLayout(grp_request)
        
        form_layout = QFormLayout()
        self.inp_method = QLineEdit("GET")
        self.inp_url = QLineEdit("http://127.0.0.1:8000")
        
        form_layout.addRow("Method:", self.inp_method)
        form_layout.addRow("URL:", self.inp_url)
        
        self.txt_req_headers = QTextEdit("User-Agent: TRON-DeCypher\nAccept: */*")
        self.txt_req_body = QTextEdit()
        
        form_layout.addRow("Headers:", self.txt_req_headers)
        form_layout.addRow("Body:", self.txt_req_body)
        
        req_layout.addLayout(form_layout)
        
        # Controls
        ctrl_layout = QHBoxLayout()
        self.chk_offline = QCheckBox("Offline Mode (Safe)")
        self.chk_offline.setChecked(True)
        self.chk_offline.stateChanged.connect(self.toggle_offline)
        
        self.inp_auth_host = QLineEdit()
        self.inp_auth_host.setPlaceholderText("Authorize Host (e.g. 127.0.0.1)")
        self.btn_auth_host = QPushButton("Authorize")
        self.btn_auth_host.clicked.connect(self.authorize_host)
        
        self.btn_send = QPushButton("Send Request")
        self.btn_send.clicked.connect(self.send_request)
        
        self.btn_parse_raw = QPushButton("Parse Raw Request Text")
        self.btn_parse_raw.clicked.connect(self.parse_raw_request)
        
        ctrl_layout.addWidget(self.chk_offline)
        ctrl_layout.addWidget(QLabel(" | "))
        ctrl_layout.addWidget(self.inp_auth_host)
        ctrl_layout.addWidget(self.btn_auth_host)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(self.btn_parse_raw)
        ctrl_layout.addWidget(self.btn_send)
        
        req_layout.addLayout(ctrl_layout)
        
        # --- BOTTOM: Response & Analysis ---
        grp_response = QGroupBox("Response Viewer & Analysis")
        res_layout = QVBoxLayout(grp_response)
        
        self.tabs = QTabWidget()
        
        # Tab: Response Body
        self.tab_body = QTextEdit()
        self.tab_body.setReadOnly(True)
        self.tabs.addTab(self.tab_body, "Response Body")
        
        # Tab: Headers & Cookies
        self.tab_headers = QTextEdit()
        self.tab_headers.setReadOnly(True)
        self.tabs.addTab(self.tab_headers, "Headers / Cookies")
        
        # Tab: HTML & JS
        self.tab_htmljs = QTextEdit()
        self.tab_htmljs.setReadOnly(True)
        self.tabs.addTab(self.tab_htmljs, "HTML / JS / JWT")
        
        # Tab: Endpoints
        self.tab_endpoints = QTextEdit()
        self.tab_endpoints.setReadOnly(True)
        self.tabs.addTab(self.tab_endpoints, "Endpoints")
        
        # Tab: Findings
        self.tab_findings = QTextEdit()
        self.tab_findings.setReadOnly(True)
        self.tabs.addTab(self.tab_findings, "Findings / IOCs")
        
        res_layout.addWidget(self.tabs)
        
        # Bottom action
        self.btn_extract_iocs = QPushButton("Force Extract IOCs to OSINT")
        self.btn_extract_iocs.clicked.connect(self.extract_iocs)
        res_layout.addWidget(self.btn_extract_iocs)
        
        # Assemble
        splitter.addWidget(grp_request)
        splitter.addWidget(grp_response)
        main_layout.addWidget(splitter)

        self.kn_panel = KnowledgePanel()
        self.kn_panel.load_knowledge("SQLi XSS Directory Traversal")
        main_layout.addWidget(self.kn_panel)

        
    def toggle_offline(self) -> None:
        safe_http_client.offline_mode = self.chk_offline.isChecked()
        if not safe_http_client.offline_mode:
            QMessageBox.warning(self, "Warning", "Offline Mode disabled! Explicit HTTP requests to authorized targets are now permitted.")
            
    def authorize_host(self) -> None:
        host = self.inp_auth_host.text().strip()
        if host:
            safe_http_client.add_authorized_host(host)
            QMessageBox.information(self, "Authorized", f"'{host}' added to authorized targets.")
            self.inp_auth_host.clear()
            
    def parse_raw_request(self) -> None:
        # Reusing the body box for raw paste temporarily
        raw = self.txt_req_body.toPlainText()
        if not raw:
            QMessageBox.information(self, "Info", "Paste raw HTTP text in the Body box first.")
            return
            
        req = raw_http_parser.parse_request(raw)
        self.inp_method.setText(req.method)
        if req.host:
            self.inp_url.setText(f"http://{req.host}{req.path}?{req.query}" if req.query else f"http://{req.host}{req.path}")
        else:
            self.inp_url.setText(f"http://unknown{req.path}")
            
        h_str = ""
        for k, v in req.headers.items():
            h_str += f"{k}: {v}\n"
        self.txt_req_headers.setText(h_str)
        self.txt_req_body.setText(req.body if isinstance(req.body, str) else "")
        
    def send_request(self) -> None:
        req = HTTPRequest(
            method=self.inp_method.text().strip(),
            url=self.inp_url.text().strip()
        )
        
        # Parse headers from box
        for line in self.txt_req_headers.toPlainText().split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                req.headers[k.strip()] = v.strip()
                
        req.body = self.txt_req_body.toPlainText()
        
        try:
            transaction = safe_http_client.send_request(req)
            self.current_response = transaction.response
            if self.current_response:
                self.display_response(self.current_response)
        except Exception as e:
            QMessageBox.critical(self, "Request Error", str(e))
            
    def display_response(self, response: HTTPResponse) -> None:
        # Body
        self.tab_body.setText(response.get_text())
        
        # Headers
        h_out = f"STATUS: {response.status_code} {response.reason}\n\nHEADERS:\n"
        for k, v in response.headers.items():
            h_out += f"{k}: {v}\n"
        h_out += "\nCOOKIES:\n"
        for k, v in response.cookies.items():
            h_out += f"{k}: {v}\n"
        self.tab_headers.setText(h_out)
        
        # Analyze
        analysis = web_analysis_service.analyze_response(response)
        
        # HTML/JS
        hj_out = "--- HTML Components ---\n"
        html_data = analysis.get("html", {})
        if html_data:
            hj_out += f"Forms: {len(html_data.get('forms', []))}\n"
            hj_out += f"Comments: {len(html_data.get('comments', []))}\n"
            for c in html_data.get('comments', []):
                hj_out += f"  <!-- {c} -->\n"
                
        hj_out += "\n--- JWTs ---\n"
        for loc, jwt in analysis.get("jwt", {}).items():
            hj_out += f"Location: {loc}\n"
            hj_out += f"Header: {jwt.get('header')}\n"
            hj_out += f"Payload: {jwt.get('payload')}\n"
            
        self.tab_htmljs.setText(hj_out)
        
        # Endpoints
        ep_out = "--- Discovered Endpoints ---\n"
        js_data = analysis.get("js", {})
        for ep in js_data.get("endpoints", []):
            ep_out += f"- {ep}\n"
            
        ep_out += "\n--- Interesting Strings ---\n"
        for s in js_data.get("interesting_strings", []):
            ep_out += f"- {s}\n"
            
        self.tab_endpoints.setText(ep_out)
        
        # Findings
        f_out = "--- Findings ---\n"
        for f in analysis.get("findings", []):
            f_out += f"{f}\n"
            
        f_out += "\n--- Extracted IOCs ---\n"
        for ioc in analysis.get("iocs", []):
            f_out += f"{ioc.ioc_type}: {ioc.value}\n"
            
        self.tab_findings.setText(f_out)
        
    def extract_iocs(self) -> None:
        if not self.current_response:
            QMessageBox.information(self, "Info", "No response loaded to extract from.")
            return
            
        text = self.current_response.get_text()
        iocs = ioc_extraction_service.extract(text, case_id="web_analysis")
        if iocs:
            QMessageBox.information(self, "IOCs", f"Extracted {len(iocs)} IOCs! Switch to OSINT view to see them.")
        else:
            QMessageBox.information(self, "IOCs", "No IOCs found in the body.")

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
