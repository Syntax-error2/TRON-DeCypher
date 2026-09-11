from datetime import UTC, datetime

from app.web.models import HTTPRequest, HTTPResponse


class RawHTTPParser:
    """Parses raw text HTTP requests and responses."""
    
    def parse_request(self, raw: str) -> HTTPRequest:
        req = HTTPRequest(timestamp=datetime.now(UTC))
        lines = raw.split("\r\n")
        if len(lines) == 1:
            lines = raw.split("\n")
            
        if not lines or not lines[0]:
            return req
            
        # Request line
        parts = lines[0].split()
        if len(parts) >= 3:
            req.method = parts[0]
            req.path = parts[1]
            if "?" in req.path:
                req.path, req.query = req.path.split("?", 1)
                
        # Headers & Body
        body_start = False
        body_lines = []
        for line in lines[1:]:
            if body_start:
                body_lines.append(line)
            elif line == "":
                body_start = True
            else:
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    req.headers[k] = v
                    if k.lower() == "host":
                        req.host = v
                    elif k.lower() == "cookie":
                        self._parse_cookies(v, req.cookies)
                    elif k.lower() == "content-type":
                        req.content_type = v
                        
        if body_lines:
            req.body = "\n".join(body_lines)
            
        return req
        
    def parse_response(self, raw: str) -> HTTPResponse:
        res = HTTPResponse(timestamp=datetime.now(UTC))
        lines = raw.split("\r\n")
        if len(lines) == 1:
            lines = raw.split("\n")
            
        if not lines or not lines[0]:
            return res
            
        # Status line
        parts = lines[0].split(" ", 2)
        if len(parts) >= 2:
            try:
                res.status_code = int(parts[1])
            except ValueError:
                pass
        if len(parts) >= 3:
            res.reason = parts[2]
            
        # Headers & Body
        body_start = False
        body_lines = []
        for line in lines[1:]:
            if body_start:
                body_lines.append(line)
            elif line == "":
                body_start = True
            else:
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    res.headers[k] = v
                    if k.lower() == "set-cookie":
                        self._parse_set_cookie(v, res.cookies)
                    elif k.lower() == "content-type":
                        res.content_type = v
                    elif k.lower() == "content-length":
                        try:
                            res.content_length = int(v)
                        except ValueError:
                            pass
                            
        if body_lines:
            res.body = "\n".join(body_lines)
            
        return res
        
    def _parse_cookies(self, cookie_header: str, cookie_dict: dict[str, str]) -> None:
        parts = cookie_header.split(";")
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                cookie_dict[k.strip()] = v.strip()
                
    def _parse_set_cookie(self, set_cookie: str, cookie_dict: dict[str, str]) -> None:
        parts = set_cookie.split(";")
        if parts and "=" in parts[0]:
            k, v = parts[0].split("=", 1)
            cookie_dict[k.strip()] = v.strip()

raw_http_parser = RawHTTPParser()
