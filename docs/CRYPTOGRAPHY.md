# Cryptography & Cryptanalysis (Phase 7)

The Cryptography module provides bounded, deterministic, and safe analysis engines for common Capture The Flag (CTF) cryptographic challenges. It operates strictly offline on user-supplied parameters or files.

## Core Architecture
- **`CryptoInput`**: A normalized wrapper supporting `text`, `bytes`, `hex`, and `base64`.
- **`CryptoResult`**: An analytical result containing `confidence`, `candidates`, `observations`, and potential plaintexts. 
- **Integration**: Designed to complement the `TransformationPipeline` (Phase 3). For example, finding an XOR key here allows the user to pipeline that transformation smoothly.

## Classical Ciphers & Heuristics
- **Identification (`CryptoIdentificationService`)**: Detects likely encodings (Base64, Hex, JWT, PEM keys) using lightweight heuristics.
- **Frequency Analysis & IoC**: Calculates English normalized Index of Coincidence (IoC). IoC > 1.5 indicates monoalphabetic ciphers, whereas IoC ~1.0 indicates random or polyalphabetic ciphers.
- **Caesar Analyzer**: Generates and scores all 26 shifts against an English frequency distance metric.

## XOR Analysis
- **Single-Byte Cracker**: Iterates 0x00–0xFF, decoding and passing payloads to the Core Text Analysis Service. Candidates are scored on their `printable_ratio` and whitespace distribution.
- **Repeating-Key Estimator**: Calculates normalized Hamming distances across sequentially sampled blocks to deduce likely key lengths.

## RSA Mathematics
- **Number Theory utilities**: Contains modular inverse (`mod_inverse`), Extended Euclidean (`egcd`), integer roots (`isqrt`), and Euler's Totient (`euler_phi`).
- **Bounded Factorization**: Employs mathematically bounded `trial_division` (with strict time limits) and `fermat_factorization` (bounded by iteration loops). 
- **Assessment Engine (`RSAAssessmentService`)**: Identifies structural weaknesses (e.g., small `e`, short modulus, near-square primes) and calculates the private exponent `d` instantly when weaknesses are confirmed.

## Modern Cryptography
- **Hash Identification (`HashAnalysisService`)**: Detects and sorts length-based hashes (MD5, SHA, BLAKE) and identifies structural hashes like `bcrypt` and `Argon2`.
- **PEM/Key Detection**: Identifies public and private RSA containers without exposing key material in logs.

## Safety & Boundaries
- **No Active Scans**: The engine cannot initiate network connections or attack external services.
- **Bounded Computation**: All mathematical operations (factorization, looping) use `time.time()` limits or explicit iteration counters to prevent freezing the application.
- **Sensitive Material**: Extracted `d` (private exponents) or passwords are held in RAM for display, but never sent to remote logging services.

## GUI (`CryptoView`)
- Offers discrete tabs for general crypto heuristics vs RSA variable plugging.
- One-click extraction of IOCs from cracked ciphertexts using the Phase 5 engine.
