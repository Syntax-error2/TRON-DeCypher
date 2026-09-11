# TRON-DeCypher Final Environment Report

## Core Environment
- **Python:** Installed and executed from env\Scripts\python.exe
- **Virtual Environment:** Active and verified
- **OS:** Windows

## Python Packages
| Package | Version | Status | Importable | Used By |
| :--- | :--- | :--- | :--- | :--- |
| PySide6 | VERIFIED | PYTHON_AVAILABLE | Yes | UI Framework |
| pydantic | VERIFIED | PYTHON_AVAILABLE | Yes | Data Models |
| pydantic_settings | VERIFIED | PYTHON_AVAILABLE | Yes | Configuration |
| httpx | VERIFIED | PYTHON_AVAILABLE | Yes | OSINT / Web / AI |
| ich | VERIFIED | PYTHON_AVAILABLE | Yes | CLI / Logging |
| python-dotenv | VERIFIED | PYTHON_AVAILABLE | Yes | Settings Persistence |
| scapy | VERIFIED | PYTHON_AVAILABLE | Yes | Network PCAP Analysis |
| Pillow | VERIFIED | PYTHON_AVAILABLE | Yes | Steganography (LSB) |
| python-magic | VERIFIED | PYTHON_AVAILABLE | Yes | File Identification |
| capstone | VERIFIED | PYTHON_AVAILABLE | Yes | Binary Disassembly |
| pefile | VERIFIED | PYTHON_AVAILABLE | Yes | Windows PE Parser |
| pyelftools | VERIFIED | PYTHON_AVAILABLE | Yes | Linux ELF Parser |
| yara-python | VERIFIED | PYTHON_AVAILABLE | Yes | Malware Static Analysis |
| cryptography | VERIFIED | PYTHON_AVAILABLE | Yes | Crypto Analysis |
| sympy | VERIFIED | PYTHON_AVAILABLE | Yes | Math / Crypto |
| gmpy2 | VERIFIED | PYTHON_AVAILABLE | Yes | High-precision Crypto |

## External Tools
All external tools (Wireshark, Ghidra, GDB, Volatility, Binwalk, etc.) are classified as EXTERNAL EXECUTABLE. The application gracefully falls back to BUILT-IN or PYTHON PACKAGE capabilities if they are NOT_INSTALLED.

## Built-in Capabilities
The following are implemented in Python natively and are always AVAILABLE:
- File Hashing
- String Extraction
- Entropy
- Decoders
- IOC Extraction
- PE / ELF Analysis (via Python packages)
- PCAP File Parsing (via scapy)
- HTTP Parser
- Triage & Artifact Management

## Network/PCAP Specifics
- **Saved PCAP/PCAPNG:** AVAILABLE (Uses scapy.utils.PcapReader)
- **Live Capture:** UNAVAILABLE (By design. Disabled to ensure offline network safety and prevent libpcap dependencies on Windows).
