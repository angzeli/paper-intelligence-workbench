# v0.7 Recommended Patch Plan

## High Priority

- Add authoring report filters for minimum claim strength, evidence type, paper status, and included-in-lit-review state.
- Add regression snapshots or stable section/count tests for the new authoring reports.
- Add explicit user-label support for conflicting claims instead of trying to infer scientific contradiction.
- Add versioned JSON schema documentation for evidence matrix exports.
- Add a CLI option to include or exclude review statements from writing packets.

## Medium Priority

- Add local HTML export for writing packets and evidence matrices.
- Add report diff tooling for authoring reports so users can compare readiness before and after note cleanup.
- Add richer paragraph-plan templates per project profile.
- Add authoring-oriented reading-list exports for papers that block a subsection.
- Add citation-bank CSV export.

## Low Priority

- Add optional Markdown callouts for Obsidian export of writing packets.
- Add theme-specific checklist integration with subsection-readiness factors.
- Add examples showing how to revise notes after a readiness report.
- Add a small command that lists all themes ranked by authoring readiness.

## Not Worth Doing Yet

- Do not generate polished literature-review prose.
- Do not infer claims from PDFs, abstracts, or titles.
- Do not use LLM APIs or remote semantic search.
- Do not add a full citation-style renderer.

## Overengineering Risks

- Making readiness scoring too complex could make the score look more authoritative than it is.
- Automatic contradiction detection would be misleading without explicit user-entered labels.
- A rich authoring UI would distract from the local-first CLI workflow until report behavior is more mature.
