import pytest

from app.web.analyzers.html_analyzer import html_analyzer
from app.web.analyzers.js_analyzer import js_analyzer
from app.web.analyzers.jwt_analyzer import jwt_analyzer
from app.web.clients.httpx_client import safe_http_client
from app.web.models import HTTPRequest
from app.web.parsers.http_parser import raw_http_parser
from app.web.utilities.redaction import secret_redaction


def test_http_parser() -> None:
    raw_req = "POST /api/login HTTP/1.1\r\nHost: example.com\r\nCookie: session=123\r\n\r\nbodycontent"
    req = raw_http_parser.parse_request(raw_req)
    assert req.method == "POST"
    assert req.path == "/api/login"
    assert req.host == "example.com"
    assert req.cookies.get("session") == "123"
    assert req.body == "bodycontent"
    
    raw_res = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nSet-Cookie: token=abc;\r\n\r\n<h1>Hello</h1>"
    res = raw_http_parser.parse_response(raw_res)
    assert res.status_code == 200
    assert res.reason == "OK"
    assert res.content_type == "text/html"
    assert res.cookies.get("token") == "abc"
    assert res.body == "<h1>Hello</h1>"
    
def test_jwt_analyzer() -> None:
    # Header: {"alg":"HS256","typ":"JWT"} -> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    # Payload: {"sub":"1234567890","name":"John Doe","iat":1516239022} -> eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    res = jwt_analyzer.analyze(jwt)
    assert res is not None
    assert res["header"]["alg"] == "HS256"
    assert res["payload"]["name"] == "John Doe"
    
def test_html_analyzer() -> None:
    html = '<html><!-- a secret comment --><form action="/post"><input name="user" type="text" value="admin"></form><script>fetch("/api/data")</script></html>'
    res = html_analyzer.analyze(html)
    assert "a secret comment" in res["comments"]
    assert len(res["forms"]) == 1
    assert res["forms"][0]["action"] == "/post"
    assert res["inputs"][0]["value"] == "admin"
    
def test_js_analyzer() -> None:
    js = 'const api = "/api/v1/users"; axios.get("/api/v2/config"); const token = "supersecret";'
    res = js_analyzer.analyze(js)
    assert "/api/v1/users" in res["endpoints"]
    assert "/api/v2/config" in res["endpoints"]
    assert "supersecret" in res["interesting_strings"]
    
def test_redaction() -> None:
    headers = {
        "Host": "example.com",
        "Authorization": "Bearer 1234567890abcdef",
        "Cookie": "session=abc"
    }
    redacted = secret_redaction.redact_headers(headers)
    assert redacted["Host"] == "example.com"
    assert redacted["Authorization"] == "Bear***************cdef"
    assert redacted["Cookie"] == "sess***=abc"  # length 11 <= 8 ? No, session=abc is 11. Wait, length 11 -> 4 + 3 + 4. "sess***=abc".

def test_safe_client_offline_mode() -> None:
    safe_http_client.offline_mode = True
    req = HTTPRequest(url="http://example.com")
    with pytest.raises(PermissionError):
        safe_http_client.send_request(req)
