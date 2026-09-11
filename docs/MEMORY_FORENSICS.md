# Memory Forensics Engine (Phase 10)

The Memory Forensics module provides offline, structured analysis of memory dumps (.raw, .vmem, .mem). It combines TRON-DeCypher's static identification and extraction layers with structured data parsed from Volatility 3 plugins (if available locally).

## Safety & Constraints
**This module performs STRICTLY offline analysis.**
- No binaries extracted from memory are executed.
- No network connections discovered in memory are actively polled or contacted.
- All extracted registry keys, variables, or command-lines are treated statically.
- The `ToolExecutionService` safely contains Volatility execution with strict timeouts.

## Analyzers
1. **Memory Identification Analyzer**: Checks the physical boundaries of the image, reading headers to identify signatures like Windows crash dumps (`PAGE`) or Linux ELF core dumps without loading the entire image into RAM.
2. **String & IOC Extraction**: Leverages the existing `StringExtractorAnalyzer` to pull text from memory, which is then routed directly to the `IOCExtractionService` to find IPs, Domains, and URLs buried in the memory space.
3. **Injection Analyzer**: Runs a heuristic pass over structured process/module data to highlight inconsistencies (e.g. `svch0st.exe` vs `svchost.exe`, or modules without backing paths).

## Volatility 3 Integration
The framework detects Volatility 3 (`vol`, `vol.py`, or `volatility3`) on the system `PATH`. When available, it securely executes the following plugins using `-r json` for structured parsing:
- `windows.pslist.PsList` -> Populates Processes and Process Tree.
- `windows.netscan.NetScan` -> Populates Network connections.
- `windows.dlllist.DllList` -> Populates Modules.

*Note: If Volatility is unavailable, the application gracefully degrades into offline string-and-heuristic mode without crashing.*

## User Interface (`MemoryView`)
A comprehensive tabbed view containing:
- **Overview**: Metadata, sizes, and architectural hints.
- **Processes**: Flat list of PIDs, PPIDs, and start times.
- **Process Tree**: A hierarchical `QTreeWidget` mapping process ancestry.
- **Network**: Local/Foreign addresses, protocols, and connection states.
- **Modules**: Base addresses and backing file paths of DLLs loaded into memory.
- **Strings**: Raw strings safely decoded from the image.
- **IOCs**: Extracted network artifacts routed to the Threat Intel panel.
- **Findings**: Observational heuristics (e.g. suspicious process names, unbacked modules).
