# Final Symbol Image Decoder Audit

## Overview
As part of the final maintenance for TRON-DeCypher v1.0.0, a complete Image-Based Symbol Cipher Decoding framework has been added to the application, adhering strictly to the constraints of the existing `Decoder` architecture and completely avoiding a "Phase 15" rewrite.

## Image Processing Pipeline
- **Segmentation**: Added `segmenter.py` using standard Pillow (`PIL`) routines. Converts images to grayscale, threshold binarizes them, and performs memory-safe BFS connected-components analysis. Extracts bounding boxes and precise symbol crops. Limits maximum processing sizes dynamically to preserve UI performance without threading locks.
- **Normalization & Hashing**: `recognizer.py` implements a scalable Mean Squared Error (MSE) grouping algorithm. Scales crops down to 16x16 and hashes identical/similar shapes (e.g., solid rectangles, circles, specific glyphs) under shared `symbol_id` tags.

## Knowledge & Profiles
- **Symbol Profiles**: `app/knowledge/symbols/profiles.json` supports definitions for Egyptian-style, Pigpen, Braille, Runes, Tap Code, and Custom Alphabets.
- **Transliteration Engine**: `solver.py` builds candidates from matched definitions or relies on the user-defined `custom_mapping`.

## Interactive Analysis
- **Mapping Editor**: The Decoder Image workspace now dynamically injects a `QTableWidget` to view detected symbols alongside their extracted ID and Count frequency. This permits on-the-fly manual dictionary generation.
- **Reading Directions**: `direction.py` tests standard parsing patterns: Left-to-Right (LR), Right-to-Left (RL), Top-to-Bottom (TB), and Bottom-to-Top (BT).

## Auto-Solve Capabilities
- `SymbolSolver` delegates translated output strings back to `TextAnalysisService.score_english()` to prioritize the correct reading direction and decipherment matrix based on classical frequency matching.
- **Flag Awareness**: Actively highlights results containing `CTF{`, `FLAG{`, or `TRON{` with a high-confidence boost and a visual `[FLAG CANDIDATE]` tag in the UI output.

## Handoff Integrations
- **[Send to Decoder]**: Automatically moves the best-scored text output back to the Decoder's text input tab, allowing chained operations like `Symbol Cipher -> Base64 -> ROT13`.
- **[Extract IOCs]**: Feeds candidate strings into the `IOCExtractionService`.
- **[Save to Case]**: Stores metrics, translation keys, and candidates into the forensic log system.

## Security Constraints Checked
- Untrusted inputs are heavily constrained; no network requests or external heuristic APIs are leveraged.
- Completely operates in memory without arbitrary file executions.

## Testing Integrity
- `test_symbol_decoder.py` guarantees synthetic shape matching, direction extraction, custom `symbol_id` overriding, and accurate auto-solve execution on bounded constraints. All `pytest` regression validations pass alongside `ruff` and `mypy` verifications.
