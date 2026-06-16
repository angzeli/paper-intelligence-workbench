# Incremental Rebuilds

`paperwb rebuild` helps larger projects decide what should be refreshed after
registry, BibTeX, note, theme, report, draft, or search-index inputs change.

The rebuild system is local and conservative. It stores content fingerprints in
`.paperwb/rebuild_metadata.json`, which is cache state and should not be
committed.

## Commands

```bash
paperwb rebuild plan --project zis_photocatalysis
paperwb rebuild status --project zis_photocatalysis
paperwb rebuild run --project zis_photocatalysis
paperwb rebuild run --project zis_photocatalysis --force
```

`plan` shows stale targets and recommended follow-up commands. `status` prints a
shorter summary. `run` records current fingerprints after you intentionally
refresh outputs.

## Targets

- `claims`: structured note inputs used by claim extraction.
- `evidence_map`: registry, BibTeX, notes, and themes used by evidence maps.
- `search_index`: local records used by the optional SQLite index.
- `report_outputs`: core report inputs.
- `manuscript_qa`: draft/manuscript QA inputs.
- `dashboard`: dashboard summary inputs.

## Safety Boundary

`paperwb rebuild run` updates rebuild metadata and records the normal ignored
local audit-log event. It does not rewrite notes, registry rows, BibTeX entries,
reports, indexes, drafts, or user comments.

Use the recommended commands from `paperwb rebuild plan` to refresh actual
outputs. Use explicit `--force` or output overwrite flags only when you intend
to replace generated files.
