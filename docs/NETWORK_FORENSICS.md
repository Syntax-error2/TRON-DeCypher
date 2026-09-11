# Network Forensics (Phase 6)

The Phase 6 Network Forensics module provides memory-bounded, passive PCAP and PCAPNG analysis, enabling offline extraction of DNS records, HTTP streams, network conversations, and extracted files.

## Core Architecture
- **Parser**: `PcapStreamingParser` iteratively reads packets via `scapy.utils.PcapReader`. This is strictly memory-safe and avoids buffering entire multi-gigabyte files into RAM.
- **Orchestrator**: `NetworkOrchestrator` feeds packets to sub-analyzers (e.g., DNS, HTTP, Convos).
- **Security constraints**: Passive only. Traffic is never replayed, URLs are never followed.

## Supported Protocols
- **Core**: Ethernet, IPv4, IPv6, TCP, UDP, ICMP.
- **Application**: DNS (A, AAAA, CNAME, TXT, MX), HTTP.
- **Extensibility**: Framework established for SMTP, POP3, FTP, TLS metadata.

## Artifact Extensibility
The Triage engine (`app/analyzers/core/file_identification.py`) inherently detects PCAP magic bytes (`\xd4\xc3\xb2\xa1` and variations) to classify network artifacts without relying on `.pcap` extensions.

## IOC Integration
The `NetworkIOCIntegrationService` pipes extracted `DNSQuery` answers, `HTTPRequest` hosts, and flow IPs straight to the Phase 5 IOC Normalizer, meaning all network metadata is automatically correlated and deduplicated.
