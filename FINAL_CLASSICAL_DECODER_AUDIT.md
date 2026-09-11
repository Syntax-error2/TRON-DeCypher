# Final Classical Decoder Audit

## Overview
As part of the final maintenance for TRON-DeCypher v1.0.0 (Phase 14 complete), a comprehensive suite of 22 Classical and Historical Ciphers has been implemented into the Decoder Workspace.

## Implemented Ciphers & Capabilities

1. **Caesar Shift** (`caesar.py`)
   - Parameters: `shift` (int), `auto_crack` (bool)
   - Features: English scoring auto-crack across 26 shifts.
2. **ROT Variants** (`rot_decoder.py`)
   - Parameters: `variant` (rot13, rot47, rot_n), `n` (int)
   - Features: Standard ASCII space shifting.
3. **Atbash** (`atbash_decoder.py`)
   - Reversible substitution mapping.
4. **Affine Cipher** (`affine.py`)
   - Parameters: `a` (int), `b` (int), `auto_crack` (bool)
   - Features: Modular inverse validation, coprime validation, brute-force cracking over valid domain pairs.
5. **Vigenère** (`vigenere.py`)
   - Parameters: `key` (str), `mode` (encrypt/decrypt)
   - Features: Key-based polyalphabetic shift.
6. **Beaufort** (`beaufort.py`)
   - Parameters: `key` (str)
   - Features: Reciprocal subtraction mapping.
7. **Autokey** (`autokey.py`)
   - Parameters: `key` (str), `mode` (encrypt/decrypt), `key_source` (plaintext/ciphertext)
8. **Playfair** (`playfair.py`)
   - Parameters: `key` (str), `mode` (encrypt/decrypt), `replace` (J=I / I=J)
   - Features: Full 5x5 matrix construction and digraphic mapping. Exposes constructed matrix in metadata.
9. **Hill Cipher** (`hill.py`)
   - Parameters: `matrix` (str), `mode` (encrypt/decrypt)
   - Features: 2x2 and 3x3 array inversion modulo 26.
10. **Polybius Square** (`polybius_based.py`)
    - Parameters: `mode`, `replace`
    - Features: Translates text to 5x5 grid coordinates.
11. **Bifid** (`fractional.py`)
    - Parameters: `key`, `period`, `mode`
12. **Trifid** (`fractional.py`)
    - Parameters: `key`, `period`, `mode`
    - Features: 3x3x3 cubic fractional transposition.
13. **Tap Code** (`polybius_based.py`)
    - Parameters: `mode`
    - Features: Converts to taps/dots or coordinate pairs based on Polybius (C/K merged).
14. **A1Z26** (`polybius_based.py`)
    - Parameters: `mode`
    - Features: Simple alphabetic numerical substitution.
15. **Rail Fence** (`transposition.py`)
    - Parameters: `rails` (int), `mode`, `auto_crack` (bool)
    - Features: Zig-zag transposition with exhaustive depth cracking.
16. **Scytale** (`transposition.py`)
    - Parameters: `columns` (int), `mode`
17. **Columnar Transposition** (`transposition.py`)
    - Parameters: `key` (str), `mode`
18. **Baconian** (`baconian.py`)
    - Parameters: `mode`, `alphabet` (standard/classic)
    - Features: 5-bit A/B binary encodings.
19. **Morse Code** (`morse_decoder.py`)
    - Parameters: `mode`
20. **Keyboard Shift** (`keyboard_shift.py`)
    - Parameters: `shift` (left/right)

## Flag-Aware Detection & Auto-Crack
- **Wrapper Safeties**: `DecoderBase.run()` was upgraded to safely intercept `CTF{...}` wrappers. The underlying cipher logic only processes the inner content, preventing destruction of the flag envelope (e.g. `CTF{KHOOR}` natively recovers to `CTF{HELLO}`).
- **Language Heuristics**: The `TextAnalysisService` was expanded to compute English frequency overlap, standard word boundaries, and common trigram prevalence. This enables `auto_crack` capabilities for Caesar, Affine, and Rail Fence by ranking generated plaintext without arbitrary API calls.

## User Interface Upgrades
The `decoder_view.py` interface was completely overhauled to categorize transformations:
- **ENCODING**
- **CLASSICAL CIPHERS**
- **NUMERIC / BITWISE**
- **TEXT / WEB**
- **HASH ANALYSIS**

A dynamic `QFormLayout` was injected directly under the dropdown. It maps the `expected_params` dict of the selected cipher to dynamic fields (`QLineEdit`, `QCheckBox`), which are injected straight into the `TransformationStep` context when executed by the Pipeline.

## Security & Architecture
- **Offline Integrity**: 100% of the cipher generation and brute-forcing relies entirely on local combinatorial operations. 
- **Modular Pipeline**: All classical ciphers extend `DecoderBase` and are immediately interoperable with standard Encoders (Base64, Hex, Compression) via the pipeline (e.g. Base64 -> Caesar -> Hex).
- **No Phase 15**: Core abstractions remain completely unviolated. Testing covers the full spectrum.
