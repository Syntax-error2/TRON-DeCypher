from typing import Any

from app.osint.extraction import ioc_extraction_service
from app.web.analyzers.html_analyzer import html_analyzer
from app.web.analyzers.js_analyzer import js_analyzer
from app.web.analyzers.jwt_analyzer import jwt_analyzer
from app.web.models import HTTPResponse


class WebAnalysisService:
    """Pipelines HTTP/Web artifact analysis."""
    
    def analyze_response(self, response: HTTPResponse) -> dict[str, Any]:
        """Runs all passive analyzers on an HTTP response."""
        
        results: dict[str, Any] = {
            "headers": response.headers,
            "cookies": response.cookies,
            "html": {},
            "js": {},
            "jwt": {},
            "iocs": [],
            "findings": []
        }
        
        # Analyze Cookies/Headers for JWTs
        for k, v in response.cookies.items():
            jwt_res = jwt_analyzer.analyze(v)
            if jwt_res:
                results["jwt"][f"cookie:{k}"] = jwt_res
                results["findings"].append(f"INFO: JWT found in cookie '{k}'")
                
        # Analyze Body based on content type
        if response.is_html:
            text = response.get_text()
            results["html"] = html_analyzer.analyze(text)
            # Find inline JS
            for s in results["html"].get("scripts", []):
                if s.startswith("Inline JS"):
                    # We can't easily extract the exact inline script here without 
                    # a full AST, but the js analyzer works on the whole HTML too.
                    pass
            js_res = js_analyzer.analyze(text)
            results["js"] = js_res
            
            for hint in results["html"].get("hints", []):
                results["findings"].append(f"LOW: {hint}")
                
        elif "javascript" in response.content_type.lower() or response.url.endswith(".js"):
            text = response.get_text()
            results["js"] = js_analyzer.analyze(text)
            if results["js"]["endpoints"]:
                results["findings"].append("INFO: Potential API endpoints discovered in JavaScript.")
                
        # Extract IOCs
        # Only parse text for IOCs to save time
        if isinstance(response.body, str) or (isinstance(response.body, bytes) and b'\x00' not in response.body[:1024]):
            text = response.get_text()
            iocs = ioc_extraction_service.extract(text, case_id="web_analysis")
            results["iocs"] = iocs
            
        return results

web_analysis_service = WebAnalysisService()
