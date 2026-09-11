from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.ai.services.copilot_service import copilot_service


class AICopilotView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_artifact_id = ""
        self.init_ui()
        
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        
        # --- Top Banner ---
        banner = QHBoxLayout()
        lbl_title = QLabel("<b>AI Copilot & Guided Analysis</b>")
        
        self.lbl_status = QLabel()
        self.update_status_indicator()
        
        btn_refresh = QPushButton("Refresh Status")
        btn_refresh.clicked.connect(self.update_status_indicator)
        
        banner.addWidget(lbl_title)
        banner.addStretch()
        banner.addWidget(self.lbl_status)
        banner.addWidget(btn_refresh)
        main_layout.addLayout(banner)
        
        # --- Context Selector ---
        ctx_layout = QHBoxLayout()
        ctx_layout.addWidget(QLabel("Current Context Artifact ID:"))
        self.txt_artifact_id = QLineEdit()
        self.txt_artifact_id.setPlaceholderText("Paste Artifact ID here to focus AI...")
        ctx_layout.addWidget(self.txt_artifact_id)
        
        btn_review = QPushButton("Review Context Before Sending")
        btn_review.clicked.connect(self.review_context)
        ctx_layout.addWidget(btn_review)
        
        main_layout.addLayout(ctx_layout)
        
        # --- Splitter (Chat | Recommendations) ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Chat area
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        chat_layout.addWidget(self.chat_history)
        
        input_layout = QHBoxLayout()
        self.txt_query = QLineEdit()
        self.txt_query.setPlaceholderText("Ask the AI about the current case or artifact...")
        self.txt_query.returnPressed.connect(self.send_query)
        
        btn_send = QPushButton("Ask")
        btn_send.clicked.connect(self.send_query)
        
        input_layout.addWidget(self.txt_query)
        input_layout.addWidget(btn_send)
        chat_layout.addLayout(input_layout)
        
        # Recommendations Area
        rec_widget = QWidget()
        rec_layout = QVBoxLayout(rec_widget)
        rec_layout.addWidget(QLabel("<b>Recommended Next Steps</b>"))
        
        self.list_recs = QListWidget()
        rec_layout.addWidget(self.list_recs)
        
        splitter.addWidget(chat_widget)
        splitter.addWidget(rec_widget)
        splitter.setSizes([600, 300])
        
        main_layout.addWidget(splitter)
        
    def update_status_indicator(self) -> None:
        copilot_service.refresh_config()
        if copilot_service.config.provider == "Anthropic":
            self.lbl_status.setText("AI: Anthropic\n● External")
            self.lbl_status.setStyleSheet("color: #4CAF50;")
        else:
            self.lbl_status.setText("AI: Mock\n○ Offline")
            self.lbl_status.setStyleSheet("color: #9E9E9E;")
            
    def review_context(self) -> None:
        art_id = self.txt_artifact_id.text().strip()
        if not art_id:
            QMessageBox.warning(self, "Context", "Please enter an Artifact ID.")
            return
            
        from app.ai.context.builder import ai_context_builder
        ctx = ai_context_builder.build_artifact_context(art_id)
        
        msg = f"Provider: {copilot_service.config.provider}\n"
        msg += f"Model: {copilot_service.config.model}\n"
        base_url = copilot_service.config.base_url or "Default"
        msg += f"Base URL: {base_url}\n"
        msg += f"Context Size: {len(ctx.text_content)} chars\n"
        msg += "Redaction Status: Enabled\n\n"
        msg += f"Preview:\n{ctx.text_content[:1000]}..."
        
        QMessageBox.information(self, "Review Context Before Sending", msg)
        
    def send_query(self) -> None:
        query = self.txt_query.text().strip()
        art_id = self.txt_artifact_id.text().strip()
        
        if not query or not art_id:
            QMessageBox.warning(self, "Input Error", "Both Artifact ID and a Query are required.")
            return
            
        self.chat_history.append(f"<b>USER:</b> {query}")
        self.txt_query.clear()
        self.txt_query.setEnabled(False)
        
        try:
            response = copilot_service.custom_query(art_id, query)
            
            self.chat_history.append(f"<b>AI ({response.confidence} Confidence):</b> {response.summary}")
            
            if response.evidence_citations:
                self.chat_history.append("<i>Evidence Cited:</i>")
                for e in response.evidence_citations:
                    self.chat_history.append(f" - {e}")
                    
            self.chat_history.append("<hr>")
            
            self.list_recs.clear()
            for rec in response.recommendations:
                item = QListWidgetItem(f"[{rec.module}] {rec.action}")
                item.setToolTip(f"Reason: {rec.reason}\nEvidence: {rec.evidence}")
                self.list_recs.addItem(item)
                
        except Exception as e:
            self.chat_history.append(f"<font color='red'><b>Error:</b> {e!s}</font>")
            
        self.txt_query.setEnabled(True)
        self.txt_query.setFocus()

    def set_case(self, case_id: str) -> None:
        self.current_case_id = case_id
