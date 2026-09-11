# File Forensics & Steganography Engine

The TRON-DeCypher Phase 4 Forensics Module enables safe, read-only analysis of imported artifacts without executing potentially malicious logic. It provides deep visibility into the structure and hidden data of common files (images, archives, executables).

## Core Principles
1. **Safety First:** No automatic payload execution, no loading external URLs, no opening documents in shell applications.
2. **Analysis Driven:** Anomalies are flagged (e.g. extension mismatch, appended data) but not automatically labeled as malware.
3. **Data Protection:** Original artifacts are never overwritten. Carving or extraction produces new child artifacts securely written to the isolated workspace.

## File Forensics
The module provides Several key analyzers:

- **MetadataAnalyzer:** Extracts filesystem properties (size, timestamps, MIME type) and safe internal formats (e.g., EXIF via Pillow).
- **FileSignatureAnalyzer:** Scans the magic bytes at various offsets to deterministically identify the true file type, guarding against extension spoofing.
- **EmbeddedDataAnalyzer:** Detects common file headers (ZIP, PDF, ELF, RAR, 7z) hiding within other binaries and checks for data appended past standard EOF markers (e.g. after a PNG `IEND` or JPEG `EOI`).
- **ImageAnalyzer:** Recursively parses PNG chunks (`IHDR`, `IDAT`, `tEXt`) verifying CRCs, and JPEG markers (`SOI`, `SOS`, `APPn`), flagging unknown anomalies.

## Hex Viewer
A custom `HexViewer` widget supports safely streaming large forensic artifacts without exhausting RAM. It displays traditional offset, hex, and ASCII views.

## Archive Extraction & Carving
- **ArchiveService:** Safely parses ZIP architectures protecting against path traversal (`../`) and absolute path extraction vulnerabilities.
- **CarvingService:** Takes a start offset and bounds to slice binary blocks out of a parent artifact, immediately hashing and registering them as tracked child artifacts linked via `parent_artifact_id`.

## Steganography Engine
The system supports foundational Stego capabilities:
- **LSB Analyzer:** Extracts Least Significant Bits (bit 0) of RGB planes, generating textual previews ranked by heuristic text printability analysis.
- **Bitplane Analyzer:** Generates distribution statistics (zero/one ratios) for all 8 bits of every color channel to assist in manual detection of high-entropy noise patterns masking data.

## Handoff to Decoder
Extracted data blocks or carved texts can be directly sent from the Forensics views into the Phase 3 **Universal Decoder Engine** for recursive unwrapping (e.g. Steganography -> Base64 -> Rot13).
