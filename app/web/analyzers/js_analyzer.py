import re


class JSAnalyzer:
    """Passively extracts strings, URLs, and potential API endpoints from JavaScript without executing it."""
    
    def analyze(self, js_text: str) -> dict[str, list[str]]:
        # Extremely basic heuristics for CTF strings
        strings = re.findall(r'["\']([^"\']{4,})["\']', js_text)
        
        endpoints = []
        interesting_strings = []
        
        for s in set(strings):
            if s.startswith(("/", "http")):
                # Potential URL/Endpoint
                endpoints.append(s)
            elif any(x in s.lower() for x in ["api", "admin", "login", "token", "secret", "key", "debug", "flag"]):
                interesting_strings.append(s)
                
        # Also grab fetch/axios signatures
        api_calls = re.findall(r'(?:fetch|axios\.get|axios\.post)\s*\(\s*["\']([^"\']+)["\']', js_text)
        for api in api_calls:
            if api not in endpoints:
                endpoints.append(api)
                
        return {
            "endpoints": sorted(set(endpoints)),
            "interesting_strings": sorted(set(interesting_strings))
        }

js_analyzer = JSAnalyzer()
