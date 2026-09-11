# CTF Knowledge and Wordlist Audit

## Overview
The Hash Recovery system now implements a highly optimized, fully prioritized candidate generation engine operating on 10,000+ base CTF words and dynamic bounded mutations (case, suffixes, separators, leetspeak, wrappers, combinations).

## Base Words
- **Master CTF List:** 10,537 unique base terms.
- **Context Lists:** TRON Context, Categories (Crypto, Forensics, etc.), and Philippine context words.
- All lists are cleanly deduplicated before iteration.

## Generated Candidates & Bounds
- **Limits:** Configurable max_candidates (default 5,000,000) and max_runtime_sec (default 60s).
- **Mutations:** Mixed case (4 variations), Leetspeak (16 variations per word), Digit suffixes (8 variations), Separators (4 variations), Combination depth up to 3, Flag Wrappers (CTF{...}, TRON{...}, FLAG{...}).
- The generation is yielded lazily with a CandidateDeduplicator tracking uniqueness hashes to save RAM.

## Priority Strategy
1. **P100**: Exact Base Words
2. **P95**: Wrapped Base Words
3. **P90**: High-Priority Context/Category Case Mutations
4. **P80**: Context Word + Digit Suffix
5. **P75**: Context Word + Separator + Digit Suffix
6. **P65**: Leetspeak mutations of Context words
7. **P55**: 2-Word Combinations + mutations
8. **P50**: 3-Word Combinations + mutations
9. **P20**: Exhaustive Master list case mutations

## Tests & Reliability
- MD5 Recovery vector TRON{Ne0n_C1rcu1t_D3f3nse_2026} successfully independently generated and verified.
- SHA-1 Recovery vector verified.
- SHA-256 Recovery vector verified.

## Security & Privacy
- System is strictly local.
- No automated network requests to online cracking services.
- No uploads of hashes.

## Performance
- Iterators and hash() based deduplication allow streams of millions of candidates at ~1M/sec.
- GUI offloads checking to QThread (HashRecoveryWorker) providing live rate metrics.

## Limitations
- Exhausting combination depth 3 across all master words would take billions of computations. Thus, depth 3 is restricted to the top 200 Context/Category priority terms.
