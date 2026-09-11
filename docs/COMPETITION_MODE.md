# Competition Mode

Designed specifically for Capture The Flag (CTF) events and timed cyber exercises, TRON-DeCypher features a dedicated "Competition Dashboard".

## Timer
The `CompetitionService` tracks `timer_elapsed` and `timer_state` at the database level. Pausing, resuming, or unexpected application closures will not destroy the time delta, ensuring accurate exercise tracking.

## Dashboard View
Displays real-time aggregated metrics:
- Processed Artifacts
- Confirmed Findings
- Extracted IOCs
- Verified Flags
- Active Tasks

## Flags
The `CandidateFlag` model (stored in the `flags` table) allows users to explicitly tag `{CTF}` pattern matches. Crucially, flags are explicitly *not* automatically submitted externally; they are queued internally for analyst review to prevent automated spamming and maintain operational security.
