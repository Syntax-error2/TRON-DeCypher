# FINAL CTF DECODER KNOWLEDGE AUDIT

## Wordlist Metrics
- **Master Wordlist (	ron_ctf_master.txt) Count:** 10,537 candidate words
- **Unique Count:** 10,537 words
- **Integrity:** Clean UTF-8. No random garbage. All derived from cyber and TRON root terms mixed with years and suffixes.

## Category Support
1. **Crypto** (ctf_crypto.txt)
2. **Forensics** (ctf_forensics.txt)
3. **Stego** (ctf_stego.txt)
4. **Network** (ctf_network.txt)
5. **Web** (ctf_web.txt)
6. **Binary** (ctf_binary.txt)
7. **Memory** (ctf_memory.txt)
8. **Malware** (ctf_malware.txt)
9. **OSINT** (ctf_osint.txt)

## Knowledge Base Architecture
- ChallengeContextManager controls challenge category dictionaries and patterns.
- FlagDetectionService automatically intercepts standard CTF{...} formats (plus TRON/FLAG) and maps them to high-confidence match blocks.
- HashRecoveryService operates efficiently as a streamed generator.

## Hash Detection Prioritization
- **Fixed:** DecoderDetectionService now properly demotes generic alphabet-based decoders (like Base64 and Hex) to low confidence if the input is identified as a strong structured hash candidate (e.g., length matches exactly 32-character hexadecimal for MD5).

## Recovery Source Priority
1. High-priority exact hits (hello, dmin, password, lag)
2. Current context category dictionary (e.g. ctf_crypto.txt if Crypto context selected)
3. ctf_tron_context.txt
4. Main massive dictionary streamed 	ron_ctf_master.txt
5. Pattern matches generated boundedly (e.g., TRON####)
6. Active bounding limits memory footprint by streaming generation logic instead of materializing trillions of mutations.

## Image Pipeline
Image detection feeds directly into OCR, QR, or Exif extractors. The derived strings pass organically into decoder_detector.detect() and trigger lag_detection_service, bringing the user a unified flag discovery capability.

## Test Results
1. 	est_wordlist_size -> Confirmed > 5000 items (Actually >10,000)
2. 	est_flag_detection -> Captured CTF{} inside strings.
3. 	est_md5_recovery -> Accurately recovered "hello"
4. 	est_sha1_recovery -> Accurately recovered "hello"
5. 	est_sha256_recovery -> Accurately recovered "hello"
6. pytest -> Full suite green across all modules (98 passing).

## Known Limitations & Security 
- **Offline Bound:** Completely strictly local. Does not upload hashes to crackstation or external lookup arrays.
- **Complexity Limit:** Capped bounding loop sizes and generator pauses protect the main thread from locking. Extremely complex passwords cannot be recovered quickly unless within dictionary bounds.
- **Fictitious Context:** "TRON Cup 2026" flags and terms are purely training-oriented logic for practical usability; this application makes NO claims of leaking actual challenge flags.
