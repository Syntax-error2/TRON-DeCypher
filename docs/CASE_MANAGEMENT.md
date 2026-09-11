# Case Management

TRON-DeCypher Phase 13 introduces a unified `CaseWorkspaceView` to orchestrate multi-artifact investigations.

## Artifact Tree
Cases group artifacts hierarchically. Decompressed ZIP files, extracted streams, and decoded outputs inherit from their parents automatically, building a visual tree of derivation.

## Tasks and Notes
The workspace contains a local tracking system:
- **Tasks**: Lightweight checklist items (`TODO`, `IN_PROGRESS`, `DONE`) prioritized (`LOW`, `HIGH`, `URGENT`) to ensure analytical gaps are closed.
- **Notes**: Categorized analytical findings (Hypothesis, Observation, Flag).

## Bookmarks
Any hex offset, string, packet, or decoded result can be bookmarked to the `bookmarks` table, attaching specific metadata and cross-referencing it directly to the root Artifact ID.

## Timelines
A linear `timeline_events` table aggregates disparate timestamped events from Forensics, Network PCAPs, AI Queries, and explicit manual bookmarks to reconstruct adversary actions accurately.
