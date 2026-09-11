# Binary Analysis & Reverse Engineering (Phase 9)

The Binary Analysis module provides a static, fully offline analysis engine tailored for CTF forensics, malware triage, and reverse engineering.

## Safety & Static Philosophy
**This module does NOT execute untrusted binaries.**
All analysis is performed completely statically via parsing headers, structures, extracting strings, and isolating disassembly. There is no active behavioral analysis, remote endpoint connection, or automatic debugger attachment that would risk infecting the host system.

## Supported Formats
- **ELF**: Supported using `pyelftools`. Extracts architectures, bitness, endianness, entry point, section headers, dynamic tags (imports), and symbols.
- **PE**: Supported using `pefile`. Extracts machine architectures, entry points, NT headers, data directories (imports/exports), and sections.
- **Mach-O**: Stub format detection is provided via magic bytes.

## Core Features
1. **API Classification**: Extracted functions are grouped into observational categories such as `Memory`, `File I/O`, `Networking`, `Registry`, and `Cryptography`.
2. **Obfuscation Analysis**: The `ObfuscationAnalyzer` assesses the entropy of the binary and individual sections, flag anomalies (like RWX sections), or indicates when sections appear to be heavily packed/compressed.
3. **Disassembly**: Using the `capstone` engine, small portions of executable sections are statically disassembled to provide an immediate look at the control flow without needing an external disassembler.
4. **Protections Status**: Statically inspects the binary headers to detect the presence of standard exploit mitigations like NX (DEP), PIE (ASLR), and Stack Canaries.
5. **String Extraction**: Re-uses the Phase 2 triage engine to extract strings, passing them dynamically to the Phase 5 IOC Extraction Engine to immediately pull out IP addresses, Domains, URLs, and File paths encoded in the binary.
6. **Tool Integration Foundation**: Contains registry detection for GDB, Ghidra, Radare2, and Rizin, as well as a stub foundation for `yara-python` integration (Phase 11).

## PySide6 GUI (`BinaryView`)
The module includes a robust GUI split into modular tabs:
- **Overview**: Format, Entry Point, Entropy, and Security Protections.
- **Sections**: Virtual Addresses, Raw Sizes, Permissions, and Section-level Entropy.
- **Imports / Exports**: Categorized imported libraries and ordinal exports.
- **Strings**: Directly extracted static printable characters.
- **Disassembly**: A direct Hex-to-Assembly preview of the executable sections.
