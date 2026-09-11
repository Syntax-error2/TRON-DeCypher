# AI Copilot & Guided Analysis (Phase 12)

The AI Copilot module acts as a strict, read-only analyst assistant designed to help human analysts synthesize complex evidence, explain findings, and discover next steps based on objective data. 

## Safety and Privacy First
- **Data Redaction**: Sensitive strings (Passwords, API Keys, JWTs) are scrubbed automatically before context transmission.
- **Explicit Consent**: Context is completely under the user's control. Artifact data is never sent externally without explicit action via the Copilot UI.
- **Read-Only Model**: The AI cannot detonate malware, fetch remote resources, or run local shell commands. Its output is limited to text explanations and structured `Recommendation` objects which users must execute manually.

## Providers
The Copilot relies on an `AIProvider` abstraction. 
- `AnthropicProvider`: An integration using the official Anthropic `messages` API endpoint.
- `MockAIProvider`: Automatically engaged when no API key is provided (`ANTHROPIC_API_KEY`), acting as a safe sandbox that generates dummy recommendations to ensure local testability.

## Context Management
LLMs perform best with tightly scoped context rather than dumping gigantic binary files. `AIContextBuilder` pulls specific artifacts and truncates findings, structured strings, and extracted IOCs to construct deterministic context.

## Structured Output & Evidence Citations
The system prompt mandates JSON-schema output enforcing strict sections:
1. `summary`: The high-level takeaway.
2. `observations`: Key analytical data points.
3. `evidence_citations`: Precise links back to the provided context (e.g., specific offset or import).
4. `recommendations`: Actionable steps linked directly to TRON-DeCypher's native tool modules (e.g. Decoder, Strings).
