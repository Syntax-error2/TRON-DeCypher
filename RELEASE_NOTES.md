# TRON-DeCypher Release Notes (v1.0.0)

**TRON-DeCypher v1.0.0** is the official, feature-complete release following the 14-Phase development cycle. 

## Features
- **Decoder**: Unified multi-format decoding (Base64, Hex, URL, Rot, CyberChef logic).
- **Forensics & Stego**: File carving, entropy visualization, LSB extraction, and nested archive traversal.
- **IOC & Threat Intel**: Native extraction of domains, IPs, URLs, hashes, and MAC addresses.
- **Network**: Passive PCAP processing parsing DNS queries, HTTP metadata, and TCP streams.
- **Crypto**: Automatic ciphertext identification and historical cipher cryptanalysis.
- **Binary/Memory**: Static triage, YARA/CAPA integrations, and offline Volatility mappings.
- **AI Copilot**: Secure, offline-capable guided analysis leveraging Mock or Anthropic models with automated data redaction.
- **Competition Mode**: Live CTF timers, flag tracking, and evidence graphs natively linked via a high-performance SQLite backend.
- **Reporting**: Professional JSON, CSV, and PDF exports with dynamic context masking.

## Security Model
- **No Automatic Execution**: Artifacts are never detonated or dynamically executed by the UI or AI.
- **Data Privacy**: AI integrations require manual user-approval of redacted contexts before transmission. No secrets are stored in the clear database.
- **Offline Capable**: The application performs 99% of its functionality entirely disconnected from the Internet. External integrations degrade gracefully.

## Limitations
- Heavily packed or obfuscated `.exe` files require external dynamic analysis environments; static CAPA hits may miss heavily encrypted overlays.
- PCAP streaming currently loads entirely into memory (Phase 6 boundary limit); >500MB PCAPs may cause degraded UI performance.

*No Phase 15. The application is feature complete.*
