# IOC Intelligence & Threat Intel (OSINT)

The Phase 5 IOC module provides robust capabilities for extracting, normalizing, deduplicating, and enriching Indicators of Compromise from static case artifacts.

## Core Principles
1. **Safety First**: No active connections to extracted domains or IPs. No external API queries occur unless explicitly authorized and an API key is configured.
2. **Offline-capable**: By default, the `Offline Mode` toggle is enabled, which forces local caching and simulated/stub returns instead of outbound network connections.
3. **Traceability**: Every extracted IOC logs its source context (the parent Artifact or Result text).

## IOC Extraction & Normalization
The `IOCExtractionService` scans string inputs for standard patterns (IPv4, IPv6, URL, Domain, MAC, Hashes) using regular expressions, followed by logical validation (e.g. `ipaddress` validation to reject `999.999.999.999`). 

The `IOCNormalizationService` guarantees consistent comparisons:
- Case-insensitivity (Domains, Emails, Hashes, MACs)
- Punctuation stripping (trailing dots)

## Provider Architecture
External data is fetched via the `ThreatIntelProvider` interface.
Stub implementations exist for:
- **VirusTotal**
- **AbuseIPDB**
- **Shodan**
- **AlienVault OTX**

When "Enrich" is invoked, the `IOCEnrichmentService` routes the IOC to applicable providers, respecting the global offline state.

## GUI Integration
A unified `OsintView` allows filtering and bulk actions on case IOCs. Furthermore, the Universal Decoder (`DecoderView`), `ForensicsView`, and `StegoView` all possess "Extract IOCs" buttons allowing users to seamlessly push generated analysis output through the OSINT pipeline.
