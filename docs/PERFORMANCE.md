# Performance Review

## 1. Startup Observations
Application initialization time is consistently under 1.5 seconds. The UI thread spins up instantly while the database `DatabaseManager.initialize()` executes safely synchronously before any heavy workers begin processing.

## 2. Hashing and Large Files
The `HashingService` utilizes fixed 64KB chunk readers. 1GB artifacts are mapped and hashed predictably without forcing memory allocation bottlenecks.

## 3. GUI Responsiveness
PySide6 handles long-running routines natively by throwing intensive operations (e.g., CAPA parsing, Entropy mapping) onto background `QThread` instances.

## 4. Known Bottlenecks
- **PCAP Parsing**: Currently blocking slightly at bounds exceeding 500MB.
- **Reporting Engine**: Enormous cases (10k+ IOCs) might take ~3-4 seconds to successfully render into the `QTextDocument` for PDF generation, but are appropriately masked behind UI loading overlays.
