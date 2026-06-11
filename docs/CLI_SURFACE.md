# CLI Surface v1.0-rc

The stable external interface for Paper Intelligence Workbench v1.0-rc is the
`paperwb` command. Commands are local-first, operate on user-provided files, and
do not call cloud APIs, LLM APIs, or publisher scrapers.

## Stable Commands

These commands are expected to remain backward-compatible across the v1.0
release line unless a release note explicitly says otherwise.

| Command | Stability | Contract |
| --- | --- | --- |
| `paperwb init` | stable | Create expected folders without overwriting existing user files |
| `paperwb validate-registry` | stable | Validate a CSV registry and optionally export JSON |
| `paperwb validate-bib` | stable | Validate local BibTeX, optionally linked to a registry |
| `paperwb add-paper` | stable | Append one manually entered registry row |
| `paperwb list` | stable | List and filter registry papers |
| `paperwb note-template` | stable | Generate a structured note without overwrite unless `--force` is used |
| `paperwb claims` | stable | Extract claims from structured Markdown notes |
| `paperwb search` | stable | Run substring search by default; indexed search only with `--indexed` |
| `paperwb report` | stable | Generate Markdown reports and refuse output overwrite unless `--force` is used |
| `paperwb writing-packet` | stable | Generate a theme-specific writing planning packet, not final prose |
| `paperwb checklist` | stable | Generate a theme review checklist |
| `paperwb doctor` | stable | Run workspace-health diagnostics |
| `paperwb project init/list/validate` | stable | Manage local project profiles under `projects/` |
| `paperwb import zotero-csv/csv/bibtex/ris` | stable | Import local bibliography data with dry-run and no silent field overwrite |
| `paperwb export` | stable | Export registries, claims, reading lists, Obsidian vaults, bundles, summaries, and report indexes |
| `paperwb index rebuild/status/clear` | stable | Manage a rebuildable local SQLite search cache |
| `paperwb files scan/status/link/unlink/audit/hash/sidecars` | stable | Inspect and link local user-provided files without deleting or scraping |
| `paperwb integrity check` | stable | Run read-only workspace integrity checks |
| `paperwb audit-log show/clear` | stable | Inspect or explicitly clear ignored local audit logs |
| `paperwb backup create/list/inspect/plan-restore/restore` | stable | Create local snapshots and plan or force restores safely |
| `paperwb migrate plan/run` | stable | Plan or copy legacy `data/` files into a new project profile without deleting originals |

## Experimental Commands

| Command | Reason |
| --- | --- |
| `paperwb synthetic generate` | Fixture schema and generated corpus shape may change as stress coverage evolves |

## Deprecated Commands

No commands are deprecated in v1.0-rc.

## Write Safety Contract

- Commands that write reports or exports refuse to overwrite existing files
  unless `--force` or the command-specific force flag is provided.
- Directory exports require a new or empty destination.
- Imports preserve existing non-empty registry fields unless the user asks for a
  documented fill behavior.
- Restore and migration workflows default to planning or dry-run behavior unless
  `--force` is passed.
- File workflows do not delete, move, copy, download, OCR, or summarize user
  documents.
- Project-profile commands keep `data/` workflow compatibility.

## Command Exit Contract

- `0`: command completed. Warnings may still be printed for incomplete local
  data.
- `1`: release or smoke script failure, usually one or more subcommands failed.
- `2`: user-facing command error such as missing input, output overwrite
  refusal, invalid project, invalid backup, or unsafe option combination.

Common errors should include what happened, where possible where it happened,
why it matters, and a next step. Python tracebacks are not expected for normal
user input errors.

## Interpretation Boundary

Reports and authoring commands organize user-entered local evidence. They do not
judge scientific truth, invent claims, invent citations, fabricate quotes, or
write polished final prose.
