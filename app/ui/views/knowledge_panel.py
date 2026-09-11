from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser, QGroupBox
from app.knowledge.knowledge_service import knowledge_service

class KnowledgePanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("CTF Knowledge Guidance", parent)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.layout.addWidget(self.browser)

    def load_knowledge(self, topic_string: str):
        results = knowledge_service.search(topic_string)
        
        if not results:
            self.browser.setHtml(f"<i>No specific guidance found for: {topic_string}</i>")
            return
            
        html = f"<h4>Relevant Guidance for: {topic_string}</h4><ul>"
        for r in results:
            topic = r.get('topic', 'General')
            text = r.get('text', '')
            source = r.get('source_type', 'Reference')
            html += f"<li><b>{topic}</b> ({source}):<br/>{text}</li>"
        html += "</ul>"
        self.browser.setHtml(html)
