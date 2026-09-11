
import dotenv
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ai.services.copilot_service import copilot_service
from app.core.config import settings


class SettingsView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        title = QLabel("TRON-DeCypher — Settings")
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        main_layout.addWidget(title)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # 1. GENERAL & PATHS TAB
        tab_general = QWidget()
        gen_layout = QVBoxLayout(tab_general)
        
        group_app = QGroupBox("Application Info")
        app_form = QFormLayout()
        app_form.addRow("Application:", QLabel(settings.app_name))
        app_form.addRow("Version:", QLabel(settings.app_version))
        self.inp_flag_pattern = QLineEdit(settings.flag_pattern)
        app_form.addRow("Flag Pattern:", self.inp_flag_pattern)

        app_form.addRow("Environment:", QLabel(settings.env))
        app_form.addRow("Log Level:", QLabel(settings.log_level))
        group_app.setLayout(app_form)
        gen_layout.addWidget(group_app)
        
        group_paths = QGroupBox("Directories")
        path_form = QFormLayout()
        
        box_cases = QHBoxLayout()
        self.txt_cases_path = QLineEdit(settings.cases_path)
        btn_cases_br = QPushButton("Browse")
        btn_cases_br.clicked.connect(lambda: self.browse_path(self.txt_cases_path))
        box_cases.addWidget(self.txt_cases_path)
        box_cases.addWidget(btn_cases_br)
        path_form.addRow("Default Case Directory:", box_cases)
        
        box_exp = QHBoxLayout()
        self.txt_exports_path = QLineEdit(getattr(settings, 'exports_path', ''))
        btn_exp_br = QPushButton("Browse")
        btn_exp_br.clicked.connect(lambda: self.browse_path(self.txt_exports_path))
        box_exp.addWidget(self.txt_exports_path)
        box_exp.addWidget(btn_exp_br)
        path_form.addRow("Default Export Directory:", box_exp)
        
        group_paths.setLayout(path_form)
        gen_layout.addWidget(group_paths)
        gen_layout.addStretch()
        self.tabs.addTab(tab_general, "General & Paths")
        
        # 2. AI COPILOT TAB
        tab_ai = QWidget()
        ai_layout = QVBoxLayout(tab_ai)
        group_ai = QGroupBox("Provider Configuration")
        ai_form = QFormLayout()
        
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["Anthropic", "Mock"])
        self.combo_provider.setCurrentText("Anthropic" if settings.anthropic_api_mode == "External" else "Mock")
        ai_form.addRow("Provider Mode:", self.combo_provider)

        self.txt_base_url = QLineEdit(settings.anthropic_base_url or "")
        self.txt_base_url.setPlaceholderText("https://api.anthropic.com/v1")
        ai_form.addRow("Base URL:", self.txt_base_url)

        self.txt_model = QLineEdit(settings.anthropic_model or "claude-3-opus-20240229")
        ai_form.addRow("Model:", self.txt_model)

        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_api_key.setPlaceholderText("Configured" if settings.anthropic_api_key else "Not Configured")
        ai_form.addRow("API Key:", self.txt_api_key)

        self.lbl_ai_status = QLabel("● Configured" if settings.anthropic_api_key else "○ Not Configured")
        if settings.anthropic_api_key:
            self.lbl_ai_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
        ai_form.addRow("Status:", self.lbl_ai_status)
        
        self.txt_temp = QLineEdit(str(settings.anthropic_temperature))
        ai_form.addRow("Temperature:", self.txt_temp)
        
        self.txt_tokens = QLineEdit(str(settings.anthropic_max_tokens))
        ai_form.addRow("Max Tokens:", self.txt_tokens)
        
        self.txt_timeout = QLineEdit(str(settings.anthropic_timeout))
        ai_form.addRow("Timeout (s):", self.txt_timeout)

        btn_test_conn = QPushButton("Test Connection")
        btn_test_conn.clicked.connect(self.test_ai_connection)
        ai_form.addRow("", btn_test_conn)

        group_ai.setLayout(ai_form)
        ai_layout.addWidget(group_ai)
        ai_layout.addStretch()
        self.tabs.addTab(tab_ai, "AI Copilot")
        
        # 3. THREAT INTEL TAB
        tab_osint = QWidget()
        osint_layout = QVBoxLayout(tab_osint)
        group_osint = QGroupBox("Threat Intelligence API Keys")
        osint_form = QFormLayout()
        
        self.txt_vt = QLineEdit()
        self.txt_vt.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_vt.setPlaceholderText("Configured" if settings.virustotal_api_key else "Not Configured")
        osint_form.addRow("VirusTotal:", self.txt_vt)
        
        self.txt_abuse = QLineEdit()
        self.txt_abuse.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_abuse.setPlaceholderText("Configured" if settings.abuseipdb_api_key else "Not Configured")
        osint_form.addRow("AbuseIPDB:", self.txt_abuse)
        
        self.txt_otx = QLineEdit()
        self.txt_otx.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_otx.setPlaceholderText("Configured" if settings.otx_api_key else "Not Configured")
        osint_form.addRow("AlienVault OTX:", self.txt_otx)
        
        self.txt_shodan = QLineEdit()
        self.txt_shodan.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_shodan.setPlaceholderText("Configured" if settings.shodan_api_key else "Not Configured")
        osint_form.addRow("Shodan:", self.txt_shodan)
        
        group_osint.setLayout(osint_form)
        osint_layout.addWidget(group_osint)
        osint_layout.addStretch()
        self.tabs.addTab(tab_osint, "Threat Intel")
        
        # 4. NETWORK & LIMITS TAB
        tab_net = QWidget()
        net_layout = QVBoxLayout(tab_net)
        
        group_net = QGroupBox("Network Safety")
        net_form = QFormLayout()
        
        self.chk_offline = QCheckBox("Enable Offline Mode")
        self.chk_offline.setChecked(getattr(settings, 'offline_mode', True))
        net_form.addRow("Offline Mode:", self.chk_offline)
        
        self.txt_http_timeout = QLineEdit(str(getattr(settings, 'http_timeout', 30)))
        net_form.addRow("HTTP Timeout (s):", self.txt_http_timeout)
        
        group_net.setLayout(net_form)
        net_layout.addWidget(group_net)
        
        group_limits = QGroupBox("Analysis Limits")
        lim_form = QFormLayout()
        
        self.txt_max_art = QLineEdit(str(getattr(settings, 'max_artifact_size', 104857600)))
        lim_form.addRow("Max Artifact Size (bytes):", self.txt_max_art)
        
        self.txt_max_pcap = QLineEdit(str(getattr(settings, 'max_pcap_packets', 100000)))
        lim_form.addRow("Max PCAP Packets:", self.txt_max_pcap)
        
        group_limits.setLayout(lim_form)
        net_layout.addWidget(group_limits)
        net_layout.addStretch()
        self.tabs.addTab(tab_net, "Network & Limits")

        # Control Buttons
        ctrl_layout = QHBoxLayout()
        btn_reset = QPushButton("Reset Defaults")
        btn_reset.clicked.connect(self.reset_defaults)
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        
        ctrl_layout.addWidget(btn_reset)
        ctrl_layout.addStretch()
        ctrl_layout.addWidget(btn_save)
        main_layout.addLayout(ctrl_layout)

    def test_ai_connection(self) -> None:
        old_mode = settings.anthropic_api_mode
        old_base = settings.anthropic_base_url
        old_key = settings.anthropic_api_key
        
        settings.anthropic_api_mode = "External" if self.combo_provider.currentText() == "Anthropic" else "Mock"
        settings.anthropic_base_url = self.txt_base_url.text()
        if self.txt_api_key.text():
            settings.anthropic_api_key = self.txt_api_key.text()
            
        copilot_service.refresh_config()
        result = copilot_service.test_connection()
        
        settings.anthropic_api_mode = old_mode
        settings.anthropic_base_url = old_base
        settings.anthropic_api_key = old_key
        copilot_service.refresh_config()
        
        if "successful" in result.lower():
            QMessageBox.information(self, "Connection Test", result)
        else:
            QMessageBox.critical(self, "Connection Test", result)

    def save_settings(self) -> None:
        try:
            env_path = ".env"
            updates = {}
            
            updates["ANTHROPIC_API_MODE"] = "External" if self.combo_provider.currentText() == "Anthropic" else "Mock"
            settings.anthropic_api_mode = updates["ANTHROPIC_API_MODE"]
            
            if self.txt_base_url.text():
                updates["ANTHROPIC_BASE_URL"] = self.txt_base_url.text()
                settings.anthropic_base_url = self.txt_base_url.text()
                
            if self.txt_model.text():
                updates["ANTHROPIC_MODEL"] = self.txt_model.text()
                settings.anthropic_model = self.txt_model.text()
                
            if self.txt_api_key.text():
                updates["ANTHROPIC_API_KEY"] = self.txt_api_key.text()
                settings.anthropic_api_key = self.txt_api_key.text()
                
            if self.txt_vt.text():
                updates["VIRUSTOTAL_API_KEY"] = self.txt_vt.text()
                settings.virustotal_api_key = self.txt_vt.text()
                
            if self.txt_abuse.text():
                updates["ABUSEIPDB_API_KEY"] = self.txt_abuse.text()
                settings.abuseipdb_api_key = self.txt_abuse.text()
                
            if self.txt_otx.text():
                updates["OTX_API_KEY"] = self.txt_otx.text()
                settings.otx_api_key = self.txt_otx.text()
                
            if self.txt_shodan.text():
                updates["SHODAN_API_KEY"] = self.txt_shodan.text()
                settings.shodan_api_key = self.txt_shodan.text()

            # For .env
            for k, v in updates.items():
                dotenv.set_key(env_path, k, v)
                
            # Direct attributes in config
            settings.cases_path = self.txt_cases_path.text()
            settings.exports_path = self.txt_exports_path.text()
            settings.offline_mode = self.chk_offline.isChecked()
            
            copilot_service.refresh_config()
            
            # UI Refresh
            self.txt_api_key.clear()
            self.txt_api_key.setPlaceholderText("Configured" if settings.anthropic_api_key else "Not Configured")
            self.lbl_ai_status.setText("● Configured" if settings.anthropic_api_key else "○ Not Configured")
            if settings.anthropic_api_key:
                self.lbl_ai_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            else:
                self.lbl_ai_status.setStyleSheet("")

            QMessageBox.information(self, "Settings", "Settings saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def reset_defaults(self) -> None:
        self.combo_provider.setCurrentText("Mock")
        self.txt_base_url.clear()
        self.txt_model.setText("claude-3-opus-20240229")
        self.chk_offline.setChecked(True)
        QMessageBox.information(self, "Reset", "Defaults restored in UI. Click Save Settings to apply.")
        
    def set_case(self, case_id: str) -> None:
        pass

    def browse_path(self, target: QLineEdit) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Directory", target.text())
        if path:
            target.setText(path)

