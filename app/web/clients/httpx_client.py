import time
from urllib.parse import urlparse

import httpx

from app.web.models import HTTPRequest, HTTPResponse, HTTPTransaction


class SafeHTTPClient:
    """Explicit, user-controlled HTTP client for CTF challenge interaction."""
    
    def __init__(self, offline_mode: bool = True):
        # By default, offline mode is True to satisfy the safety rule.
        self.offline_mode = offline_mode
        self.authorized_hosts: set[str] = set()
        
    def add_authorized_host(self, host: str) -> None:
        self.authorized_hosts.add(host.lower())
        
    def send_request(self, request: HTTPRequest) -> HTTPTransaction:
        if self.offline_mode:
            raise PermissionError("Offline mode is active. Explicitly disable it in settings to send HTTP requests.")
            
        target_url = request.url
        if not target_url:
            # Reconstruct from parts
            scheme = request.scheme or "http"
            host = request.host
            if not host:
                raise ValueError("Host or URL must be provided.")
            port_str = f":{request.port}" if request.port not in (80, 443) else ""
            target_url = f"{scheme}://{host}{port_str}{request.path}"
            if request.query:
                target_url += f"?{request.query}"
                
        parsed = urlparse(target_url)
        if parsed.hostname and parsed.hostname.lower() not in self.authorized_hosts:
            raise PermissionError(f"Target host '{parsed.hostname}' is not in the authorized targets list.")
            
        start_time = time.time()
        
        # Prepare httpx content
        content = request.body.encode('utf-8') if isinstance(request.body, str) else request.body if request.body else None
            
        res = HTTPResponse()
        res.url = target_url
        
        try:
            with httpx.Client() as client:
                resp = client.request(
                    method=request.method,
                    url=target_url,
                    headers=request.headers,
                    cookies=request.cookies,
                    timeout=10.0,
                    follow_redirects=False,
                    content=content
                )
                
            res.status_code = resp.status_code
            res.reason = resp.reason_phrase
            res.headers = dict(resp.headers)
            res.cookies = dict(resp.cookies)
            res.body = resp.content
            res.content_type = resp.headers.get("Content-Type", "")
            res.content_length = len(resp.content)
            
        except httpx.RequestError as exc:
            res.reason = f"Request Error: {exc}"
            
        duration = time.time() - start_time
        
        return HTTPTransaction(
            request=request,
            response=res,
            duration=duration,
            source="manual"
        )
        
safe_http_client = SafeHTTPClient()
