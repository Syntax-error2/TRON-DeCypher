from typing import Any

from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter


def export_pdf(data: dict[str, Any], path: str) -> None:
    html = "<h1>TRON-DeCypher Case Report</h1>"
    
    case_info = data.get("case", {})
    html += f"<h2>Case: {case_info.get('name', 'Unknown')}</h2>"
    html += f"<p>Description: {case_info.get('description', '')}</p>"
    
    html += "<h2>Findings</h2><ul>"
    for f in data.get("findings", []):
        html += f"<li><b>[{f.get('severity', 'INFO')}] {f.get('title', '')}</b>: {f.get('description', '')}</li>"
    html += "</ul>"
    
    html += "<h2>Artifacts</h2><ul>"
    for a in data.get("artifacts", []):
        html += f"<li>{a.get('filename', '')} (SHA256: {a.get('sha256', '')})</li>"
    html += "</ul>"
    
    doc = QTextDocument()
    doc.setHtml(html)
    
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(path)
    
    doc.print_(printer)
