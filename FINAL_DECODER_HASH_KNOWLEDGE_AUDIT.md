# FINAL DECODER HASH KNOWLEDGE AUDIT

This document summarizes the high-end CTF hash analysis, local recovery, and knowledge base integration inside the TRON-DeCypher Decoder module.

## Supported Hash Algorithms
The updated HashFormatRegistry supports identification and local verification for:
- MD4, MD5
- SHA-1, SHA-224, SHA-256, SHA-384, SHA-512
- SHA-512/224, SHA-512/256
- SHA3-224, SHA3-256, SHA3-384, SHA3-512
- BLAKE2b, BLAKE2s
- RIPEMD-160
- LM, NTLM

## Structured Formats
We also detect and parse prefixes (e.g. $2b$, $argon2id$) for:
- bcrypt
- Argon2
- SHA512-Crypt ($6$), SHA256-Crypt ($5$), MD5-Crypt ($1$)
- scrypt ($scrypt$, $7$)
- PBKDF2 ($pbkdf2$, $p5k2$)
- phpass ($P$, $H$)

## Detection Accuracy
- Uses deterministic regex matching and length mapping.
- Exact prefix matches (structured) yield a 95% confidence score.
- Standard hex digests (e.g., 64-char hex) map to SHA-256 (90% confidence), with secondary alternatives (e.g., SHA3-256, BLAKE2s) at 70%.
- Ambiguities are properly disclosed in the UI. We do not claim certainty when multiple hash types use the exact same digest size.

## Automatic Recovery Engine
The Decoder now provides a seamless "Recover Hash" workflow entirely local to the machine:
1. **CTF Built-in Dictionary**: A locally stored file (pp/knowledge/dictionaries/ctf_common.txt) containing generic CTF training words (e.g., lag, 	ron, cyber, dmin). 
2. **Wordlist Support**: The engine supports line-by-line reading of user-provided wordlists, managing memory carefully.
3. **Bounded Mutations**: The background generator automatically tests common variations on dictionary words: lower/upper/capitalize, reverse, append 123/1234/2026, prepend 123, separators (_, -), and leetspeak substitution (->4, e->3).
4. **Patterns**: Simple wildcard mask checks (e.g., TRON####, FLAG####) are dynamically expanded to digit combinations within strict combinatoric limits.

## CTF Knowledge Base and Challenge Context
A new foundational knowledge architecture has been initialized:
- ChallengeContext: allows categorizing the active analysis (e.g., Web, Crypto, Forensics).
- Configurable lag_patterns parameterize the automatic CTF Flag Detection. If a recovered hash matches TRON{...} or FLAG{...}, the engine intercepts the match and flags it explicitly.
- We deliberately use *generic* training terms and do not claim official/secret TRON 2026 data.

## Image and Multi-Mode Input
The Decoder natively supports:
- **Text Mode**: Standard string transformations and hash analysis.
- **Image Mode**: Extracts metadata, dimensions, formats, and displays a preview. The Image Tools panel allows triggering OCR, QR/Barcode, Stego (LSB), and IOC extraction from the image payload.
- **File Mode**: Generic file ingest for specific binary analyzers.

All image and web functionality operates completely locally; no unexpected external uploads, no shell execution, and no blind URL chasing.

## Performance and Safety
- Hashing is strictly offloaded to an asynchronous QThread (HashRecoveryWorker).
- The GUI remains responsive, rendering live count-per-second and elapsed time updates.
- Cancellations gracefully interrupt the worker.
- Combinatorial explosions in wildcard patterns are strictly capped before execution.

## Testing
Comprehensive testing guarantees standard functionality:
- 92 passing synthetic tests via Pytest.
- MyPy strict compliance and Ruff linting rules enforced.
- Re-tested Decoder transformations (Base64, Hex, ROT13, etc.) ensure no regression.
- Security verification confirmed that no external brute-force APIs (like CrackStation) are ever queried.

## Known Limitations
- Password hashes (bcrypt, Argon2) currently only report identification and structure layout. They intentionally do not attempt offline cracking due to extreme hardware/memory requirements, aligning with the "CTF/Training safe" mandate.
- High-combinatoric masks (e.g., ?a?a?a?a?a?a?a?a in Hashcat notation) are blocked; only highly bounded masks (TRON####) are evaluated inline.
