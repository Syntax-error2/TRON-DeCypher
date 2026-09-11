# TRON-DeCypher Final Decoder Maintenance Report

## New Transformations Added
1. **Base58** (Bitcoin Alphabet)
2. **Base85** (b85 & a85 variants)
3. **Punycode**
4. **JSON Escapes**
5. **Gzip, Zlib, Deflate** (Compression handling)
6. **JWT Decode**
7. **Decimal ASCII & Octal ASCII**
8. **Bitwise NOT & Byte Swap**
9. **Reverse String / Bytes**
10. **Whitespace Normalization**
11. **Bacon Cipher & Beaufort Cipher**

## Hash Support
- Integrated **Hash Generation** via a robust HashingService wrapper.
- Supported Algorithms: md5, sha1, sha224, sha256, sha384, sha512, sha3_256, sha3_512, lake2b, lake2s, crc32.
- Integrated **Hash Identification** utilizing lengths, charset validation, and confidence scores (e.g., distinguishing 64-character hex as SHA-256 vs SHA3-256).

## Detection Improvements
- Auto-detection models now evaluate: JSON Escapes, Decimal/Octal ASCII representations, Punycode, Base58, Gzip/Zlib Magic Bytes, and standard JWT configurations (eyJ...).
- Implemented protection logic that ensures one-way hashes are isolated and not inadvertently pushed into reversible UI workflows.

## UI Changes
- Decoded View transformed into a modular QTabWidget containing:
  - **Transformations Tab**: Retains the pipeline builder but incorporates a searchable dropdown matrix for filtering transformations.
  - **Hash & Digest Tab**: Dedicated tab to Identify hashes, load binary files safely to generate checksums, and a comparison validator to quickly match against known hashes.
- Enhanced UX with bounding limits on text inputs to prevent hard locking on massive payload ingestions.

## Pipeline Changes
- DecoderBase now requires declarations for category, eversible, input_types, output_types, and description.
- HashResult and HashCandidate models introduced to represent cryptanalytic one-way artifacts vs. standard reversible transforms.

## Testing & Regressions
- Unit test coverage heavily expanded (	est_decoder_expansion.py tests all new decoders, UI fallback limits, and hashing logic).
- Passed full regression block: 81/81 tests passing.
- Ruff static analysis cleared.
- Mypy --strict compliance achieved for the entire application.

## Performance
- **Hash Chunking:** Large files hash securely utilizing CHUNK_SIZE = 64KB, guaranteeing low RAM utilization regardless of input size.
- **Fast Lookup:** Regex mapping prevents the UI thread from hanging on heavy string decodings (like Bacon).

## Remaining Limitations
- Zlib compression bomb (zip bomb) mitigation relies on native zlib boundaries; highly nested decompression requires user timeout bounds inside PyQt threads.
- Beaufort Cipher does not yet extract candidate keys without user-provided key material.
