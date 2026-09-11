# Reporting Engine

The Reporting Engine consolidates structured SQLite evidence into portable formats suitable for executive delivery or external machine parsing.

## Available Formats
1. **JSON Export**: Contains a completely structured dump of the `cases`, `artifacts`, `findings`, `iocs`, and `timeline` payload.
2. **CSV Export**: Outputs tabular analytical data (Findings, IOCs) for easy ingestion into spreadsheets or SIEMs.
3. **PDF Export**: Generates a professional visual report via `QTextDocument` and `QPrinter`, ensuring fidelity directly from the GUI without requiring heavyweight dependencies.

## Data Redaction
The engine shares the `AIDataRedactor` logic from Phase 12. If `mask_sensitive_data` is enabled (which it is by default), all JWTs, known Bearer signatures, and passwords extracted from Strings/Forensics are aggressively scrubbed before being written to disk, preventing accidental secret leakage in distributed reports.
