# Web & HTTP Challenge Analysis (Phase 8)

The Web Analysis module provides a secure, fully offline-by-default environment for analyzing HTTP traffic, parsing raw web artifacts (HTML, JS, JWTs, HTTP Requests), and manually interacting with authorized CTF challenge endpoints.

## Core Architecture
- **`HTTPRequest`, `HTTPResponse`, `HTTPTransaction`**: Immutable dataclasses representing the structure of a web transaction.
- **Offline Safety First**: By default, the `SafeHTTPClient` rejects all outbound network requests. Users must explicitly uncheck `Offline Mode` and authorize a target host (e.g. `127.0.0.1`) before requests are allowed.
- **No Background execution**: The system deliberately lacks automated crawling, fuzzing, or JS evaluation to prevent sandbox escapes and accidental attacks.

## Parsers
- **`RawHTTPParser`**: Consumes raw HTTP text strings (e.g., from a proxy or packet capture) and splits them into typed `HTTPRequest`/`HTTPResponse` objects.
- **`RobotsSitemapParser`**: Extracts paths passively from `robots.txt` and `sitemap.xml`.

## Analysis Engines
- **HTML (`HTMLAnalyzer`)**: Employs `html.parser.HTMLParser` to securely extract comments, form boundaries, inputs, and inline scripts without executing them.
- **JavaScript (`JSAnalyzer`)**: Uses regex heuristics to find strings resembling URLs, endpoints (e.g., `/api/admin`), or interesting keys (e.g., `supersecret`).
- **JWT (`JWTAnalyzer`)**: Dissects 3-part base64 strings into header and payload JSON dictionaries. Deliberately does not verify signatures to avoid active crypto brute-forcing.

## Secret Redaction
- **`SecretRedactionUtility`**: Masks values of headers like `Authorization` and `Cookie` (e.g., `Bear***************cdef`) to ensure CTF flags and active session tokens are not permanently leaked into the SQLite logs.

## Pipeline Integration
- Discovered endpoints and interesting strings can be directly pushed to the Phase 5 **OSINT / IOC Extraction Engine**.
- Plaintext bodies can be forwarded to the Phase 3 **Decoder Engine** for rapid base64/hex transformations.
- Complete transactions are recorded in the SQLite `web_history` table for case persistence.
