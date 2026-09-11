# TRON-DeCypher

TRON-DeCypher is a comprehensive, offline, deterministic Capture The Flag (CTF) toolkit and analysis framework. It is designed to assist cybersecurity analysts and CTF competitors with decoding, hashing, cryptography, steganography, forensics, and more—all from a unified native desktop application.

## 🚀 Features

*   **Decoder / Crypto Engine**: Automatically identifies and decodes dozens of formats including Base64/32/58/85, Classical Ciphers (Caesar, Vigenère, Affine, etc.), Binary, Hex, URLs, and more.
*   **Hash Recovery**: Advanced deterministic hash cracking capable of analyzing target context, leetspeak generation, suffixes, and flag wrappers (e.g., \CTK{...}\).
*   **Image & Symbol Analysis**: Steganography extraction (LSB), metadata carving, and symbol-cipher evaluation.
*   **Forensics & Network**: Extensible modules for analyzing PE/ELF binaries, PCAP files, and file signatures.
*   **CTF Knowledge Base**: An integrated offline FTS (Full-Text Search) engine containing cheatsheets, methodologies, and workflows.
*   **AI Copilot**: Optional LLM integration (Anthropic, etc.) for contextual analysis and automated triage.

## 🛠️ Installation (Source)

TRON-DeCypher is built using Python 3.13 and PySide6.

1. Clone the repository:
   \\\ash
   git clone https://github.com/yourusername/TRON-DeCypher.git
   cd TRON-DeCypher
   \\\
2. Install dependencies:
   \\\ash
   pip install -r requirements.txt
   # OR using flit / pip directly from pyproject.toml
   pip install -e .
   \\\
3. Run the application:
   \\\ash
   python -m app.main
   \\\

## 📦 Releases

You can download the compiled standalone executable for Windows from the [Releases](../../releases) page.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
