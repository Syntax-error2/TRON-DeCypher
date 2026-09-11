from html.parser import HTMLParser
from typing import Any


class PassiveHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.comments: list[str] = []
        self.scripts: list[str] = []
        self.forms: list[dict[str, Any]] = []
        self.inputs: list[dict[str, Any]] = []
        
        self._current_form: dict[str, Any] | None = None
        self._in_script = False
        
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = {k.lower(): v for k, v in attrs}
        
        if tag == "form":
            self._current_form = {
                "action": attr_dict.get("action", ""),
                "method": attr_dict.get("method", "GET"),
                "inputs": []
            }
            self.forms.append(self._current_form)
            
        elif tag == "input":
            input_data = {
                "name": attr_dict.get("name", ""),
                "type": attr_dict.get("type", "text"),
                "value": attr_dict.get("value", "")
            }
            self.inputs.append(input_data)
            if self._current_form:
                self._current_form["inputs"].append(input_data)
                
        elif tag == "script":
            src = attr_dict.get("src")
            if src:
                self.scripts.append(f"Source: {src}")
            else:
                self._in_script = True
                
    def handle_endtag(self, tag: str) -> None:
        if tag == "form":
            self._current_form = None
        elif tag == "script":
            self._in_script = False
            
    def handle_data(self, data: str) -> None:
        if self._in_script and data.strip():
            self.scripts.append(f"Inline JS (length: {len(data)})")
            
    def handle_comment(self, data: str) -> None:
        if data.strip():
            self.comments.append(data.strip())

class HTMLAnalyzer:
    """Passively extracts components from HTML text."""
    
    def analyze(self, html_text: str) -> dict[str, Any]:
        parser = PassiveHTMLParser()
        try:
            parser.feed(html_text)
        except Exception:
            pass
            
        # Basic search heuristics
        hints = []
        lower_html = html_text.lower()
        if "flag{" in lower_html or "flag_" in lower_html:
            hints.append("Potential flag pattern observed.")
        if "password" in lower_html or "secret" in lower_html:
            hints.append("References to passwords or secrets observed.")
            
        return {
            "comments": parser.comments,
            "forms": parser.forms,
            "inputs": parser.inputs,
            "scripts": parser.scripts,
            "hints": hints
        }

html_analyzer = HTMLAnalyzer()
