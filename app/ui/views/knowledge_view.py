import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.knowledge.knowledge_service import knowledge_service


class CTFKnowledgeView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()
        
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Top bar: Search and Filter
        top_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search knowledge (e.g., Caesar, Ghidra, Wireshark, sqlmap)...")
        self.txt_search.returnPressed.connect(self.perform_search)
        
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(["All", "Crypto", "Web", "Reverse", "Pwn", "Forensics", "Stego", "Network", "OSINT", "Archive", "Misc"])
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self.perform_search)
        
        self.btn_import = QPushButton("Import Knowledge")
        self.btn_import.clicked.connect(self.import_document)
        
        top_layout.addWidget(QLabel("Search:"))
        top_layout.addWidget(self.txt_search)
        top_layout.addWidget(QLabel("Category:"))
        top_layout.addWidget(self.cmb_category)
        top_layout.addWidget(self.btn_search)
        top_layout.addWidget(self.btn_import)
        
        layout.addLayout(top_layout)
        
        # Splitter for Results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Results Group
        grp_results = QGroupBox("Search Results")
        results_layout = QVBoxLayout(grp_results)
        self.txt_results = QTextEdit()
        self.txt_results.setReadOnly(True)
        results_layout.addWidget(self.txt_results)
        splitter.addWidget(grp_results)
        
        # Tools Group
        grp_tools = QGroupBox("Tools & Commands (REFERENCE ONLY)")
        tools_layout = QVBoxLayout(grp_tools)
        self.txt_tools = QTextEdit()
        self.txt_tools.setReadOnly(True)
        tools_layout.addWidget(self.txt_tools)
        splitter.addWidget(grp_tools)
        
        # Workflows Group
        grp_workflows = QGroupBox("Workflows")
        wf_layout = QVBoxLayout(grp_workflows)
        self.txt_workflows = QTextEdit()
        self.txt_workflows.setReadOnly(True)
        wf_layout.addWidget(self.txt_workflows)
        splitter.addWidget(grp_workflows)
        
        layout.addWidget(splitter)
        
        # Initial load
        self.perform_search()
        
    def perform_search(self) -> None:
        query = self.txt_search.text().strip()
        category = self.cmb_category.currentText()
        
        if category == "All":
            if query:
                chunks = knowledge_service.search(query)
            else:
                chunks = []
        else:
            chunks = knowledge_service.search_category(category, query)
            
        # Display Chunks
        out_html = "<h3>Topic Results</h3>"
        if not chunks:
            if query:
                out_html += "<p>No matching material was found in the imported references.</p>"
            else:
                out_html += "<p>Enter a query to search.</p>"
        else:
            for c in chunks:
                out_html += f"<b>Topic:</b> {c['topic']}<br>"
                out_html += f"<b>Source:</b> {c['source']} (Page {c['page']})<br>"
                out_html += f"<b>Category:</b> {c['category']} ({c['source_type']})<br>"
                out_html += f"<b>Summary:</b> {c['text']}<br>"
                if c['tool_names']:
                    out_html += f"<b>Mentioned Tools:</b> {c['tool_names']}<br>"
                out_html += "<hr>"
        self.txt_results.setHtml(out_html)
        
        # Search Tools & Commands
        tools = knowledge_service.search_tool(query) if query else []
        cmds = knowledge_service.search_command(query) if query else []
        
        tool_html = "<h3>Tools & Commands</h3>"
        if not tools and not cmds:
            tool_html += "<p>No tools/commands found.</p>"
        else:
            for t in tools:
                tool_html += f"<b>Tool:</b> {t['tool']} - {t['purpose']}<br>"
                tool_html += f"<b>Source:</b> {t['source']} (Page {t['page']})<br><br>"
            
            for c in cmds:
                tool_html += f"<b>Command:</b> <pre>{c['command']}</pre><br>"
                tool_html += f"<b>Purpose:</b> {c['purpose']}<br>"
                tool_html += f"<b>Source:</b> {c['source']} (Page {c['page']})<br>"
                tool_html += "<i>Requires Explicit Execution. Reference Only.</i><br><br>"
        self.txt_tools.setHtml(tool_html)
        
        # Workflows
        wfs = knowledge_service.get_workflow(category if category != "All" else query)
        wf_html = "<h3>Workflows</h3>"
        if not wfs:
            wf_html += "<p>No workflows found.</p>"
        else:
            for w in wfs:
                wf_html += f"<b>{w['title']} ({w['category']})</b><br>"
                wf_html += f"<b>Source:</b> {w['source']}<br>"
                wf_html += f"<pre>{w['steps']}</pre><br><hr>"
        self.txt_workflows.setHtml(wf_html)
        
    def import_document(self) -> None:
        # Prompt for file
        path, _ = QFileDialog.getOpenFileName(self, "Import Knowledge Document", "", "Documents (*.pdf *.txt *.md *.html)")
        if path:
            QMessageBox.information(self, "Import", f"Document {os.path.basename(path)} imported and indexed successfully (Mocked).")

